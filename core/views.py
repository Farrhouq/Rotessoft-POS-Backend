from django.shortcuts import render

# Create your views here.
# use viewsets and the models to get me some crud operations

from rest_framework import viewsets, status
from .models import Store, Product, ProductSale, Sale
from .serializers import StoreSerializer, ProductSerializer, ProductSaleSerializer, SaleSerializer
from rest_framework.response import Response

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

        # self.serializer_class().create(request.data)
        # return super().create(request, *args, **kwargs)
        # Serialize the incoming data
        serializer = self.get_serializer(data=request.data)

        # Check if the data is valid
        serializer.is_valid(raise_exception=True)

        # Save the validated data, creating the object
        self.perform_create(serializer, extra_data=request.data['sales'])

        # Return a response with the newly created object and a 201 status
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer, extra_data):
        serializer.save(sales=extra_data)
