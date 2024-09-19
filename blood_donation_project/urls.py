from django.urls import path, include
from rest_framework.routers import DefaultRouter
from delivery.views import DeliveryStaffViewSet, DeliveryViewSet, DeliveryIssueViewSet, register_user, confirm_email

router = DefaultRouter()
router.register(r'delivery-staff', DeliveryStaffViewSet)
router.register(r'deliveries', DeliveryViewSet)
router.register(r'delivery-issues', DeliveryIssueViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/register/', register_user, name='register'),
    path('api/auth/confirm-email/<uuid:token>/', confirm_email, name='confirm_email'),
]