from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class DeliveryStaff(AbstractUser):
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    email_confirmed = models.BooleanField(default=False)
    confirmation_token = models.UUIDField(default=uuid.uuid4, editable=False)

class Delivery(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('picked_up', 'Picked Up'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    delivery_staff = models.ForeignKey(DeliveryStaff, on_delete=models.CASCADE)
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    pickup_time = models.DateTimeField()
    blood_type = models.CharField(max_length=10)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    qr_code = models.CharField(max_length=100, unique=True)

class DeliveryIssue(models.Model):
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE)
    description = models.TextField()
    photo = models.ImageField(upload_to='issue_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)