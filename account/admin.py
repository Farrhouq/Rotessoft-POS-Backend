from django.contrib import admin
from account.models import StaffUserProfile, AdminUserProfile, User
from django.contrib.auth.admin import UserAdmin

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(AdminUserProfile)
