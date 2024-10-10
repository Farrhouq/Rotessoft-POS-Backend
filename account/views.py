from rest_framework import viewsets, status
from .models import StaffUserProfile, AdminUserProfile
from .serializers import StaffUserProfileSerializer, AdminUserProfileSerializer
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


class AdminUserProfileViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = AdminUserProfile.objects.all()
    serializer_class = AdminUserProfileSerializer

    # def create(self, request, *args, **kwargs):
    #         serializer = self.get_serializer(data=request.data)
    #         serializer.is_valid(raise_exception=True)  # This will raise an error if validation fails
    #         self.perform_create(serializer)  # This calls serializer.save() and thus the serializer's create method
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)

class StaffUserProfileViewSet(viewsets.ModelViewSet):
    queryset = StaffUserProfile.objects.all()
    serializer_class = StaffUserProfileSerializer
