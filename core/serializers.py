from account.models import StaffUserProfile
from rest_framework import serializers
from .models import Store, Product, ProductSale, Sale
from django.db.models import Sum, Count, F
from django.utils import timezone
from datetime import timedelta
from account.models import User


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
    # total = serializers.SerializerMethodField()

    # def get_total(self, obj):
    #     return 5
    #     # return obj.total

    class Meta:
        model = Sale
        fields = ["created_at", "product_string", "total", "store", "id"]

    def validate(self, data):
        return data

    def create(self, validated_data):
        product_sales = []
        sales = validated_data.pop('sales')
        id = validated_data["id"]
        store = validated_data['store']
        created_at = validated_data['created_at']
        customer_name = validated_data.get('customer_name')
        made_by_user_id = validated_data['made_by'] # the user who made the sale (might be the admin, or one of the staff. Multiple staff will be possible in the future)

        try:
            made_by_user = User.objects.get(id=made_by_user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")

        new_sale = Sale.objects.create(store=store, created_at=created_at, id=id,
            sale_made_by=made_by_user, customer_name=customer_name)

        sale_total = 0
        product_names_list = []
        for sale in sales:
            product_id = sale['id']
            product = Product.objects.get(id=product_id)

            if product.amount_in_stock < int(sale['quantity']):
                new_sale.delete()
                raise serializers.ValidationError(f"Not enough stock for product {product.name} ({product.amount_in_stock} in stock)")
            product_sale = ProductSale.objects.create(product=product, quantity=int(sale['quantity']), previous_quantity=product.amount_in_stock, sale=new_sale)
            sale_total += sale['quantity'] * product.selling_price
            product_names_list.append(product.name)
            product.amount_in_stock = F("amount_in_stock") - int(sale['quantity'])
            product.save()

        new_sale.total = sale_total
        new_sale.product_string = ", ".join(product_names_list)
        new_sale.save()

        return new_sale
