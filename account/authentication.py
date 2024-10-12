from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailOrPhoneBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in using either their phone number or email.
    """
    def authenticate(self, request=None, username=None, password=None, **kwargs):
        # Check if the username is an email or phone number
        try:
            if '@' in username:
                user = User.objects.get(email=username)
            else:
                user = User.objects.get(phone_number=username)
        except User.DoesNotExist:
            return None

        # Verify the password
        if user.check_password(password):
            return user

        return None
