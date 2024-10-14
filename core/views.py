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

class DashboardView(APIView):
    def get(self, request):
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

class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def create(self, request, *args, **kwargs):
        store = request.user.staffuserprofile.store
        request.data['store'] = store.id
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        # if self.request.user.role == 'staff': # I'm hoping the user is always a staff
        return super().get_queryset().filter(store=self.request.user.staffuserprofile.store)


class ProductSaleViewSet(viewsets.ModelViewSet):
    queryset = ProductSale.objects.all()
    serializer_class = ProductSaleSerializer


class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer

    def create(self, request, *args, **kwargs):
        request.data['store'] = request.user.staffuserprofile.store.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer, extra_data=request.data['sales'])
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer, extra_data):
        serializer.save(sales=extra_data)
