from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.core.exceptions import ValidationError

class User(AbstractUser):
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    username = models.CharField(max_length=150, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.full_clean() # This will call the clean method to validate the data
        if self.email:
            self.username = self.email
        else:
            self.username = self.phone_number
        super().save(*args, **kwargs)  # Proceed with saving the user

    @property
    def role(self):
        if hasattr(self, 'adminuserprofile'):
            return 'admin'
        if hasattr(self, 'staffuserprofile'):
            return 'staff'

    def __str__(self):
        if self.email:
            return self.email
        return self.phone_number

    def clean(self):
        if self.email:
            if User.objects.exclude(pk=self.pk).filter(email=self.email).exists():
                raise ValidationError("This email is already in use.")

        if self.phone_number:
            if User.objects.exclude(pk=self.pk).filter(phone_number=self.phone_number).exists():
                raise ValidationError("This number is already in use.")

        if not self.email and not self.phone_number:
            raise ValidationError("Either email or phone number must be provided.")

class AdminUserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=200, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    brand_name = models.CharField(max_length=200, null=True)
    # updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return str(self.user)


class StaffUserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    store = models.ForeignKey('core.Store', on_delete=models.CASCADE)
    address = models.CharField(max_length=200, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
