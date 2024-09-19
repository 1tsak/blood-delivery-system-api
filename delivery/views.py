from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from .models import DeliveryStaff, Delivery, DeliveryIssue
from .serializers import DeliveryStaffSerializer, DeliverySerializer, DeliveryIssueSerializer

class DeliveryStaffViewSet(viewsets.ModelViewSet):
    queryset = DeliveryStaff.objects.all()
    serializer_class = DeliveryStaffSerializer
    permission_classes = [permissions.IsAuthenticated]

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
    permission_classes = [permissions.IsAuthenticated]

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
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(delivery__delivery_staff=self.request.user)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = DeliveryStaffSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def confirm_email(request, token):
    try:
        user = DeliveryStaff.objects.get(confirmation_token=token)
        user.email_confirmed = True
        user.save()
        return Response({"message": "Email confirmed successfully"})
    except DeliveryStaff.DoesNotExist:
        return Response({"error": "Invalid token"}, status=400)