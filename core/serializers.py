from rest_framework import serializers
from .models import Store, Product, ProductSale, Sale


class StoreSerializer(serializers.ModelSerializer):
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
    class Meta:
        model = Sale
        fields = "__all__"

    def validate(self, data):
        print(data)
        return data

    def create(self, validated_data):
        print(validated_data)
        sales = validated_data.pop('sales')
        product_sales = []
        store = validated_data['store']
        new_sale = Sale.objects.create(store=store)
        for sale in sales:
            product_id = sale['id']
            product = Product.objects.get(id=product_id)
            product_sale = ProductSale.objects.create(product=product, quantity=int(sale['quantity']), sale=new_sale)
        return new_sale
