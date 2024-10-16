# otp_app/views.py
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework import generics, status
from rest_framework.response import Response
from .models import OTP
import random
import string
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny


User = get_user_model()

class SendOTPView(generics.CreateAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('username')
        # Check if user exists
        try:
            user = User.objects.get(username=email)
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        otp = ''.join(random.choices(string.digits, k=6)) # Generate a 6-digit OTP

        # Save the OTP associated with the user
        OTP.objects.create(user=user, otp=otp)
        user.set_password(otp)
        user.save()

        # Send email with the OTP
        # send_mail(
        #     'Your OTP Code',
        #     f'Your OTP code is {otp}',
        #     'from@example.com',  # Replace with your email
        #     [email],
        #     fail_silently=False,
        # )
        if not user.is_superuser:
            print("\n==============\nYour OTP is ", otp, "\n==============\n") # replace with code for sending otp
            return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)
        return Response({"message": "OTP sent successfully", "otp": otp}, status=status.HTTP_200_OK)


class VerifyOTPView(generics.CreateAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        otp = request.data.get('otp')

        try:
            otp_instance = OTP.objects.get(user__username=username, otp=otp, is_used=False)

            if otp_instance.is_expired():
                return Response({"message": "OTP has expired"}, status=status.HTTP_400_BAD_REQUEST)

            # Mark OTP as used
            otp_instance.is_used = True
            otp_instance.save()

            # Authenticate the user
            user = otp_instance.user
            refresh = RefreshToken.for_user(user)
            refresh['role'] = user.role
            access = refresh.access_token
            access['role'] = user.role

            return Response({"message": "Login successful!",
                "refresh": str(refresh), "access": str(access)}, status=status.HTTP_200_OK)

        except OTP.DoesNotExist:
            return Response({"message": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
