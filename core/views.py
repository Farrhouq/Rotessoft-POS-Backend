from django.shortcuts import render

# Create your views here.
# use viewsets and the models to get me some crud operations

from rest_framework import viewsets
from .models import Store, Product, ProductSale, Sale
from .serializers import StoreSerializer, ProductSerializer, ProductSaleSerializer, SaleSerializer


class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductSaleViewSet(viewsets.ModelViewSet):
    queryset = ProductSale.objects.all()
    serializer_class = ProductSaleSerializer


class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
