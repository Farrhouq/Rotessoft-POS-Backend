from rest_framework.routers import DefaultRouter
from .views import StaffUserProfileViewSet, AdminUserProfileViewSet, UserLoginView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from django.urls import path

router = DefaultRouter()

router.register(r"staff", StaffUserProfileViewSet)
router.register(r"admins", AdminUserProfileViewSet)

urlpatterns = [
    path('api/token/', UserLoginView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

urlpatterns += router.urls
