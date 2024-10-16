from django.shortcuts import render

# Create your views here.
# use viewsets and the models to get me some crud operations

from rest_framework import viewsets, status
from rest_framework.views import APIView
from .models import Store, Product, ProductSale, Sale
from .serializers import StoreSerializer, ProductSerializer, ProductSaleSerializer, SaleSerializer
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum, Count, F
from django.db.models.functions import TruncDay
from datetime import timedelta
from rest_framework.permissions import AllowAny
from otp.models import OTP
import random
import string
from rest_framework_simplejwt.tokens import RefreshToken

from account.serializers import *
from account.models import *

class DashboardView(APIView):
    def get(self, request):
        store = self.request.query_params.get('store', None)
        if store:
            store = Store.objects.get(id=store)
        if request.user.role == 'staff':
            store = request.user.staffuserprofile.store
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())  # Monday
        end_of_week = start_of_week + timedelta(days=6)  # Sunday
        # Get the last 7 days' range
        start_of_range = today - timedelta(days=6)  # 7 days ago
        end_of_range = today

        # 1. Total sales for the day
        today_sales = ProductSale.objects.filter(sale__created_at__date=today, sale__store=store)
        total_sales_today = today_sales.aggregate(
            total=Sum(F('quantity') * F('product__price'))
        )['total'] or 0

        # 2. Total sales for the current week grouped by day
        # week_sales = ProductSale.objects.filter(sale__created_at__date__range=[start_of_week, end_of_week])
        # daily_sales = week_sales.values('sale__created_at__date').annotate(
        #     total=Sum(F('quantity') * F('product__price'))
        # ).order_by('sale__created_at__date')

        # 2. Total sales for each of the last 7 days
        last_7_days_sales = ProductSale.objects.filter(sale__created_at__date__range=[start_of_range, end_of_range], sale__store=store)
        daily_sales = last_7_days_sales.values('sale__created_at__date').annotate(
            total=Sum(F('quantity') * F('product__price'))
        ).order_by('sale__created_at__date')

        # 3. Top products for the current week
        # top_products = ProductSale.objects.filter(
        #     sale__created_at__date__range=[start_of_week, end_of_week]
        # ).values('product__name').annotate(
        #     total_quantity=Sum('quantity'),
        #     total_sales=Sum(F('quantity') * F('product__price'))
        # ).order_by('-total_quantity')[:5]

        # 3. Top products for the last 7 days
        top_products_7_days = ProductSale.objects.filter(
            sale__created_at__date__range=[start_of_range, end_of_range], sale__store=store
        ).values('product__name').annotate(
            total_quantity=Sum('quantity'),
            total_sales=Sum(F('quantity') * F('product__price'))
        ).order_by('-total_quantity')[:5]

        # Prepare the response data
        response_data = {
            "total_sales_today": total_sales_today,
            "daily_sales": daily_sales,  # List of daily sales totals for the week
            "top_products": top_products_7_days,  # List of top 5 products based on quantity sold
            "daily_target": store.daily_target
        }

        return Response(response_data)


class NewBusinessRegistrationView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        if not request.user.is_superuser:
            return Response({"message": "You are not authorized to perform this action"}, status=status.HTTP_403_FORBIDDEN)

        data = request.data['data']
        first_name = data['firstName']
        last_name = data['lastName']
        email_or_phone = data['emailPhone']
        address = data['address']
        business_name = data['businessName']
        businessLocation = data['businessLocation']
        daily_target = data['dailyTarget']

        # create an admin user
        email = None
        phone_number = None
        if '@' in email_or_phone:
            email = email_or_phone
        else:
            phone_number = email_or_phone

        otp = ''.join(random.choices(string.digits, k=6))
        try:
            admin_user = User.objects.create_user(email_or_phone, email, otp, first_name=first_name, last_name=last_name, phone_number=phone_number)
            OTP.objects.create(user=admin_user, otp=otp)
            admin_user.set_password(otp)
            admin_user.save()
            admin_profile = AdminUserProfile.objects.create(user=admin_user, address=address)
            store = Store.objects.create(name=business_name,
                location=businessLocation, daily_target=daily_target, admin=admin_profile)
        except:
            return Response({"message": "An error occurred!"}, status.HTTP_400_BAD_REQUEST)
            # return Response({"message": "Registration successful"}, status.HTTP_200_OK)

        # send the otp
        print("\n==============\nYour OTP is ", otp, "\n==============\n")

        return Response({"message": "Registration successful"}, status.HTTP_200_OK)

class StoreViewSet(viewsets.ModelViewSet):
    # permission_classes = # needs to be set to something like ForAdminOnly (in terms of user.role)
    queryset = Store.objects.all()
    serializer_class = StoreSerializer

    def get_queryset(self):
        return super().get_queryset().filter(admin=self.request.user.adminuserprofile)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        store = self.request.query_params.get('store')
        if store and self.request.user.role == 'admin':
            return super().get_queryset().filter(store=store)
        if self.request.user.role == 'staff': # I'm hoping the user is always a staff
            return super().get_queryset().filter(store=self.request.user.staffuserprofile.store)


class ProductSaleViewSet(viewsets.ModelViewSet):
    queryset = ProductSale.objects.all()
    serializer_class = ProductSaleSerializer


class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer

    def get_queryset(self):
        store = self.request.query_params.get('store')
        if store:
            return super().get_queryset().filter(store=store, created_at__date=timezone.now().date())
        return super().get_queryset().filter(store=self.request.user.staffuserprofile.store, created_at__date=timezone.now().date())

    def create(self, request, *args, **kwargs):
        request.data['store'] = request.user.staffuserprofile.store.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer, extra_data=request.data['sales'])
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer, extra_data):
        serializer.save(sales=extra_data)
