from django.db import models
from account.models import AdminUserProfile, StaffUserProfile


class Store(models.Model):
    name = models.CharField(max_length=200)
    admin = models.ForeignKey(AdminUserProfile, on_delete=models.CASCADE, related_name="stores")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    daily_target = models.FloatField(default=1000)
    location = models.CharField(max_length=200, null=True)

    def __str__(self):
        return str(self.name)


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    selling_price = models.FloatField()
    cost_price = models.FloatField()
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    amount_in_stock = models.PositiveIntegerField()

    class Meta:
        unique_together = ('name', 'store')

    def __str__(self):
        return self.name


class Sale(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    created_at = models.DateTimeField()
    customer_name = models.CharField(max_length=200, null=True, blank=True)
    amount_paid = models.FloatField(null=True, blank=True)


    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        products = self.products.all()
        return ", ".join([product.product.name for product in products])

    @property
    def total(self):
        return sum([(product.quantity * product.product.selling_price) for product in self.products.all()])

class ProductSale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="products")
    quantity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
