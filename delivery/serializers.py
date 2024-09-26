from rest_framework import serializers
from .models import DeliveryStaff, Delivery, DeliveryIssue

class DeliveryStaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryStaff
        fields = ['id', 'email', 'password', 'first_name', 'last_name', 'phone_number', 'address', 'email_confirmed', 'gender', 'license_number', 'vehicle_type', 'vehicle_number', 'dob']
        extra_kwargs = {
            'password': {'write_only': True},
            'email_confirmed': {'read_only': True},
            'email': {'required': True}
        }

    def create(self, validated_data):
        user = DeliveryStaff.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            **{k: v for k, v in validated_data.items() if k not in ('email', 'password')}
        )
        return user

class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = '__all__'

class DeliveryIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryIssue
        fields = '__all__'