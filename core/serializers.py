from account.models import StaffUserProfile
from rest_framework import serializers
from .models import Store, Product, ProductSale, Sale
from django.db.models import Sum, Count, F
from django.utils import timezone
from datetime import timedelta


class StoreSerializer(serializers.ModelSerializer):
    today_total = serializers.SerializerMethodField()
    week_total = serializers.SerializerMethodField()
    overall_total = serializers.SerializerMethodField()
    staff_id = serializers.SerializerMethodField()

    def get_today_total(self, obj):
        today = timezone.now().date()
        today_sales = ProductSale.objects.filter(sale__created_at__date=today, sale__store=obj)
        total_sales_today = today_sales.aggregate(
            total=Sum(F('quantity') * F('product__selling_price'))
        )['total'] or 0
        return total_sales_today

    def get_week_total(self, obj):
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        week_sales = ProductSale.objects.filter(sale__created_at__date__range=[start_of_week, end_of_week], sale__store=obj)
        total_sales_week = week_sales.aggregate(
            total=Sum(F('quantity') * F('product__selling_price'))
        )['total'] or 0
        return total_sales_week

    def get_overall_total(self, obj):
        overall_sales = ProductSale.objects.filter(sale__store=obj)
        total_sales_overall = overall_sales.aggregate(
            total=Sum(F('quantity') * F('product__selling_price'))
        )['total'] or 0
        return total_sales_overall

    def get_staff_id(self, obj):
        try:
            return StaffUserProfile.objects.get(store=obj).id#.values_list('id', flat=True)
        except StaffUserProfile.DoesNotExist:
            return None

    class Meta:
        model = Store
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class ProductSaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSale
        fields = "__all__"


class SaleSerializer(serializers.ModelSerializer):
    total = serializers.SerializerMethodField()

    def get_total(self, obj):
        return obj.total

    class Meta:
        model = Sale
        fields = ["created_at", "__str__", "total", "store", "id"]

    def validate(self, data):
        return data

    def create(self, validated_data):
        print("heere")
        print(validated_data, "\n\n-------------------------------------\n\n")
        sales = validated_data.pop('sales')
        product_sales = []
        store = validated_data['store']
        created_at = validated_data['created_at']
        # id = validated_data["id"]
        print(id)
        new_sale = Sale.objects.create(store=store, created_at=created_at)
        for sale in sales:
            product_id = sale['id']
            product = Product.objects.get(id=product_id)

            if product.amount_in_stock < int(sale['quantity']):
                new_sale.delete()
                raise serializers.ValidationError(f"Not enough stock for product {product.name} ({product.amount_in_stock} in stock)")
            product_sale = ProductSale.objects.create(product=product, quantity=int(sale['quantity']), sale=new_sale)
            product.amount_in_stock = F("amount_in_stock") - int(sale['quantity'])
            product.save()

        return new_sale
