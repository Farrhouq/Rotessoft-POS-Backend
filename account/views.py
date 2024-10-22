from rest_framework import viewsets, status
from .models import StaffUserProfile, AdminUserProfile
from .serializers import StaffUserProfileSerializer, AdminUserProfileSerializer, UserLoginSerializer
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics

class AdminUserProfileViewSet(viewsets.ModelViewSet):
    queryset = AdminUserProfile.objects.all()
    serializer_class = AdminUserProfileSerializer


class StaffUserProfileViewSet(viewsets.ModelViewSet):
    queryset = StaffUserProfile.objects.all()
    serializer_class = StaffUserProfileSerializer


class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # Validate the input data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get the authenticated user
        user = serializer.validated_data['user']

        # Create JWT tokens
        refresh = RefreshToken.for_user(user)

        # Include the user's role in the JWT claims
        refresh['role'] = user.role

        # You can also add the role to the access token if needed
        access = refresh.access_token
        access['role'] = user.role

        return Response({
            'refresh': str(refresh),
            'access': str(access),
        })
