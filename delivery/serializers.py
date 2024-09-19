from rest_framework import serializers
from .models import DeliveryStaff, Delivery, DeliveryIssue

class DeliveryStaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryStaff
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'address', 'email_confirmed']
        extra_kwargs = {'password': {'write_only': True}, 'email_confirmed': {'read_only': True}}

    def create(self, validated_data):
        user = DeliveryStaff.objects.create_user(**validated_data)
        # Send confirmation email here
        return user

class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = '__all__'

class DeliveryIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryIssue
        fields = '__all__'