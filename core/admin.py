from django.contrib import admin
from core.models import Store, Sale, Product, ProductSale

# Register your models here.
admin.site.register(Store)
admin.site.register(Sale)
admin.site.register(Product)
admin.site.register(ProductSale)
