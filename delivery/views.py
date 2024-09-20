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
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

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

class DeliveryIssueViewSet(viewsets.ModelViewSet):
    queryset = DeliveryIssue.objects.all()
    serializer_class = DeliveryIssueSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(delivery__delivery_staff=self.request.user)

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