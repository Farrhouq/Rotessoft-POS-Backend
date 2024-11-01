from rest_framework import serializers
from .models import StaffUserProfile, AdminUserProfile, User
from django.core.exceptions import ValidationError as DjangoValidationError
from .authentication import EmailOrPhoneBackend

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        user = EmailOrPhoneBackend().authenticate(**attrs)
        if not user:
            raise serializers.ValidationError('Invalid credentials')
        attrs['user'] = user  # Attach the authenticated user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number', 'password', 'first_name', 'last_name']
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
            first_name=validated_data.get('first_name', ""),
            last_name=validated_data.get('last_name', "")
        )

        # Set and hash the user's password
        user.set_password(validated_data['password'])

        try:
            user.save()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        return user

    def update(self, user, validated_data):
        user.email = validated_data.get('email', "")
        user.phone_number = validated_data.get('phone_number', "")
        user.first_name = validated_data.get('first_name', "")
        user.last_name = validated_data.get('last_name', "")

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
        user_data = validated_data.pop('user')
        print(user_data)
        user = UserSerializer().create(validated_data=user_data)
        admin_profile = AdminUserProfile.objects.create(user=user, **validated_data)
        return admin_profile


class StaffUserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = StaffUserProfile
        fields = "__all__"

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        staff_profile = StaffUserProfile.objects.create(user=user, **validated_data)
        return staff_profile

    def update(self, username, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.get(username=username)
        user = UserSerializer().update(user=user, validated_data=user_data)
        staff_profile = user.staffuserprofile
        staff_profile.address = validated_data.get("address")
        staff_profile.save()
        return staff_profile
