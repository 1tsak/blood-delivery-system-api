from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import DeliveryStaff, Delivery, DeliveryIssue
from .serializers import DeliveryStaffSerializer, DeliverySerializer, DeliveryIssueSerializer
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
import uuid

User = get_user_model()

class DeliveryStaffViewSet(viewsets.ModelViewSet):
    queryset = DeliveryStaff.objects.all()
    serializer_class = DeliveryStaffSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['GET', 'PUT'])
    def me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = self.get_serializer(request.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeliveryViewSet(viewsets.ModelViewSet):
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Delivery.objects.filter(delivery_staff=self.request.user)

    @action(detail=True, methods=['POST'])
    def update_status(self, request, pk=None):
        delivery = self.get_object()
        status = request.data.get('status')
        if status in dict(Delivery.STATUS_CHOICES):
            delivery.status = status
            delivery.save()
            return Response({'status': 'Delivery status updated'})
        return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST'])
    def scan_qr(self, request, pk=None):
        delivery = self.get_object()
        qr_data = request.data.get('qr_data')
        if delivery.qr_code == qr_data:
            if delivery.status == 'pending':
                delivery.status = 'picked_up'
                delivery.save()
                return Response({'status': 'Delivery picked up'})
            else:
                return Response({'error': 'Delivery is not in pending status'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Invalid QR code'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST'])
    def confirm_delivery(self, request, pk=None):
        delivery = self.get_object()
        if delivery.status == 'picked_up':
            delivery.status = 'completed'
            delivery.save()
            return Response({'status': 'Delivery confirmed'})
        return Response({'error': 'Delivery is not in picked up status'}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        delivery = serializer.save(delivery_staff=self.request.user)
        send_push_notification(
            self.request.user.fcm_token,
            "New Delivery Assignment",
            f"You have a new delivery to {delivery.dropoff_location}"
        )

class DeliveryIssueViewSet(viewsets.ModelViewSet):
    queryset = DeliveryIssue.objects.all()
    serializer_class = DeliveryIssueSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)

    def get_queryset(self):
        return DeliveryIssue.objects.filter(delivery__delivery_staff=self.request.user)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = DeliveryStaffSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.is_active = False
        user.confirmation_token = str(uuid.uuid4())
        user.save()

        # Send confirmation email
        send_mail(
            'Confirm your email',
            f'Please click this link to confirm your email: {settings.SITE_URL}/confirm-email/{user.confirmation_token}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        return Response({"message": "User registered. Please check your email to confirm registration."}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def confirm_email(request, token):
    try:
        user = User.objects.get(confirmation_token=token)
        user.is_active = True
        user.confirmation_token = ''
        user.save()
        return Response({"message": "Email confirmed. You can now log in."}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"message": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    email = request.data.get('email')
    try:
        user = User.objects.get(email=email)
        reset_token = str(uuid.uuid4())
        user.password_reset_token = reset_token
        user.save()

        # Send password reset email
        send_mail(
            'Password Reset Request',
            f'Please click this link to reset your password: {settings.SITE_URL}/reset-password/{reset_token}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        return Response({"message": "Password reset email sent."}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"message": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request, token):
    new_password = request.data.get('new_password')
    try:
        user = User.objects.get(password_reset_token=token)
        user.set_password(new_password)
        user.password_reset_token = ''
        user.save()
        return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"message": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)