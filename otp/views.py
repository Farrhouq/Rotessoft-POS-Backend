# otp_app/views.py
from gzip import READ
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework import generics, status
from rest_framework.response import Response
from .models import OTP
import random
import string
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from django.conf import settings
import requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


User = get_user_model()

class SendOTPView(generics.CreateAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('username')
        # Check if user exists
        try:
            print(email, "email")
            user = User.objects.get(username=str(email).strip())
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        otp = ''.join(random.choices(string.digits, k=6)) # Generate a 6-digit OTP

        # Save the OTP associated with the user
        OTP.objects.create(user=user, otp=otp)
        user.set_password(otp)
        user.save()

        if user.is_superuser: # send otp via response for superusers
            return Response({"message": "OTP sent successfully", "otp": otp}, status=status.HTTP_200_OK)

        if settings.PLATFORM == "local": # send otp in terminal in local environment
            print("\n==============\nYour OTP is ", otp, "\n==============\n")
            return Response({"message": "OTP sent successfully"})


        # send email for non-superusers.
        if user.email:
            send_email_otp(otp, user.email)
            print(f"otp {otp} sent to {user.email}")
            return Response({"message": "OTP sent successfully"})

        # send sms for non-superusers.
        elif user.phone_number:
            sms_phone = user.phone_number
            if len(sms_phone) == 10 and sms_phone[0] == '0': # eg: 0596421143
                sms_phone = '233' + sms_phone[1:] # ==> 233596421143
                message = send_otp_sms(otp, sms_phone)
                return Response({"message": message}, status=status.HTTP_200_OK)

            if sms_phone[0:3] == '233' and len(sms_phone) == 12: # eg: 233596421143
                message = send_otp_sms(otp, user.phone_number)
                return Response({"message": message}, status=status.HTTP_200_OK)

            return Response({"message": "Invalid phone number format"})



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

            store_name = ""
            if user.role == "admin":
                store_name = user.adminuserprofile.brand_name
            elif user.role == "staff":
                store_name = user.staffuserprofile.store.name

            return Response({"message": "Login successful!",
                "refresh": str(refresh), "access": str(access), "store_name": store_name}, status=status.HTTP_200_OK)

        except OTP.DoesNotExist:
            return Response({"message": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)


def send_otp_sms(otp_code, phone_number):
    client = requests.Session()
    message = f"Your Rotessoft POS verification code is {otp_code}."
    API_KEY = settings.ARKESEL_API_KEY

    # Send SMS
    member_url = f"https://sms.arkesel.com/sms/api?action=send-sms&api_key={API_KEY}&to={phone_number}&from={"ROTESSOFT"}&sms={message}"
    response = client.get(member_url)
    response.raise_for_status()
    if int(response.status_code) not in range(200, 300):
        return f"{phone_number} - {response.json()['message']}"
    return f"SMS sent to {phone_number}"


def send_email_otp(otp_code, email):
    API_KEY = settings.SENDGRID_API_KEY
    message = Mail(
        from_email='farouqimoro@gmail.com',
        to_emails=email,
        subject='Rotessoft POS Verification code',
        html_content=f"Your Rotessoft POS verification code is <strong>{otp_code}</strong>."
    )
    try:
        sg = SendGridAPIClient(API_KEY)
        response = sg.send(message)
        print("sent successful")
    except Exception as e:
        return str(e)
