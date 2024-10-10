from rest_framework import serializers
from .models import StaffUserProfile, AdminUserProfile, User
from django.core.exceptions import ValidationError as DjangoValidationError


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        """
        Ensure either email or phone number is provided.
        """
        email = data.get('email', None)
        phone_number = data.get('phone_number', None)

        if not email and not phone_number:
            raise serializers.ValidationError("Either email or phone number must be provided.")

        return data

    def create(self, validated_data):
        """
        Create user with either email or phone number.
        """
        user = User(
            username=validated_data.get('username'),
            email=validated_data.get('email', ""),  # Use email if provided, else empty string
            phone_number=validated_data.get('phone_number', ""),  # Use phone_number if provided
        )

        # Set and hash the user's password
        user.set_password(validated_data['password'])

        try:
            user.save()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        return user

class AdminUserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = AdminUserProfile
        fields = "__all__"

    def create(self, validated_data):
            print(validated_data)
            user_data = validated_data.pop('user')
            print(user_data)
            user = UserSerializer.create(UserSerializer(), validated_data=user_data)
            admin_profile = AdminUserProfile.objects.create(user=user, **validated_data)
            return admin_profile


class StaffUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffUserProfile
        fields = "__all__"

    def create(self, validated_data):
            user_data = validated_data.pop('user')
            user = UserSerializer.create(UserSerializer(), validated_data=user_data)
            staff_profile = StaffUserProfile.objects.create(user=user, **validated_data)
            return staff_profile
