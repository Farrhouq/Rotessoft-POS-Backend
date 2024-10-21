from django.contrib import admin
from account.models import StaffUserProfile, AdminUserProfile, User
from django.contrib.auth.admin import UserAdmin
from django.conf import settings

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(AdminUserProfile)
admin.site.register(StaffUserProfile)

admin.site.site_header = settings.SITE_HEADER
