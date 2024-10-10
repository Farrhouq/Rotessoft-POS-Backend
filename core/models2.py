import uuid
from decimal import Decimal
from datetime import datetime

from django.db import models
from django.db.models import UniqueConstraint
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.db.models.signals import pre_delete, post_save

from account.models import AdminProfile, StaffProfile, CustomerProfile

from utils.models import DiscountTypeChoices, PaymentMethodChoices, get_deleted_product, get_deleted_staff_profile, get_deleted_customer_profile

# Create your models here.


def store_logo_dir(instance, filename):
    return '/'.join(['stores', str(instance.id), 'logos', filename])


class Store(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    admin_profile = models.ForeignKey(
        AdminProfile, on_delete=models.CASCADE, related_name="stores")
    store_name = models.CharField(max_length=200, null=False, blank=False)
    email = models.EmailField(max_length=200)
    contact = models.CharField(max_length=200)
    branch_name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    logo = models.ImageField(upload_to=store_logo_dir, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # store manager

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['store_name', 'branch_name'], name='unique_store_name_branch')
        ]

    def __str__(self):
        return f"{self.store_name} - {self.branch_name}"


class ProductBrand(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="product_brands")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


class ProductCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category_name = models.CharField(max_length=200)
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="product_categories")

    def __str__(self):
        return self.category_name


def product_images_dir(instance, filename):
    return '/'.join(['stores', str(instance.store.id), 'products', str(instance.id), f"{str(instance)}.{filename.split('.')[-1]}"])


class Product(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference_id = models.CharField(max_length=20, editable=False, null=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    brand = models.ForeignKey(ProductBrand, on_delete=models.CASCADE,
                              blank=True, null=True, related_name="products")
    category = models.ForeignKey(
        ProductCategory, on_delete=models.SET_NULL, related_name='products', null=True)
    image = models.ImageField(
        max_length=200, blank=True, null=True, upload_to=product_images_dir)
    cost_price = models.DecimalField(decimal_places=2, max_digits=10)
    selling_price = models.DecimalField(decimal_places=2, max_digits=10)
    discount_type = models.CharField(
        max_length=20, choices=DiscountTypeChoices.choices, default=DiscountTypeChoices.CASH)
    discount_value = models.IntegerField(default=0, blank=True)
    quantity_in_stock = models.IntegerField()
    minimum_alert_quantity = models.IntegerField(default=0)
    publiished = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['product_name', 'store'],
                             name='unique_productname_storeid')
        ]

    def __str__(self):
        return self.product_name


@receiver(post_save, sender=Product)
def set_reference_id(sender, instance, created, **kwargs):
    if created and not instance.reference_id:
        store_id_part = str(instance.store.id)[:2]
        date_part = datetime.now().strftime('%m%y')
        uuid_part = str(instance.id).split('-')[0]
        instance.reference_id = f"PR{store_id_part}{
            uuid_part[:2].upper()}{date_part}"
        instance.save()


class Sale(models.Model):
    """
    A Sale holds all information about a customer's purchase
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # readable sale reference
    reference_id = models.CharField(
        max_length=15, unique=True, editable=False, null=True)
    salesperson = models.ForeignKey(StaffProfile, related_name="sales", on_delete=models.SET(
        get_deleted_staff_profile), null=True)
    customer_profile = models.ForeignKey(CustomerProfile, related_name="purchases", on_delete=models.SET(
        get_deleted_customer_profile), null=True)
    store = models.ForeignKey(
        Store, related_name="sales", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    discount_type = models.CharField(
        max_length=20, choices=DiscountTypeChoices.choices, default=DiscountTypeChoices.CASH)
    discount_value = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(
        max_length=20, choices=PaymentMethodChoices.choices, default=PaymentMethodChoices.CASH)

    class Meta:
        ordering = ['-created_at']

    @property
    def sub_total(self):
        return sum([item.subtotal for item in self.sale_items.all()])

    @property
    def total_bill(self):
        # TODO: This should calculate the amount due after discount has been applied
        # TODO: It should calculate appropriately based on the type; PERCENTAGE or CASH
        if self.discount_type == "PERCENTAGE":
            # Ensure that discount_value is converted to a Decimal before the calculation
            discount_decimal = Decimal(self.discount_value) / Decimal(100)

            # Perform the calculation with Decimal types
            return self.sub_total - (self.sub_total * discount_decimal)

        else:
            return Decimal(self.sub_total) - Decimal(self.discount_value)

    def __str__(self) -> str:
        return f"{self.id}"

    def save(self, *args, **kwargs):
        # ? We need to save each sale item so that
        # ? the unit_price and
        if not self.reference_id:  # implementation may be changed in future
            store_id = str(self.store.id)[:2]
            date_part = datetime.now().strftime('%m%y')
            uuid_part = str(self.id).split('-')[0]
            self.reference_id = f"SL{store_id}{
                uuid_part[:2].upper()}{date_part}"

        super().save(*args, **kwargs)
        for item in self.sale_items.all():
            item.save()

    def clean(self):
        if self.salesperson and not self.salesperson.user.groups.filter(name="STAFF").exists():
            raise ValidationError(
                {'salesperson': 'Salesperson must belong to the STAFF group'})

        # !
        # if self.customer and not self.customer.groups.filter(name="CUSTOMER").exists():
        #     raise ValidationError({'customer': 'Customer must belong to the CUSTOMER group'})

        super().clean()

    def remove_sale_item(self, item_id):
        try:
            item = self.sale_items.get(id=item_id)
            item.delete()
            self.save()  # Optionally, save the sale to recalculate the total
        except SaleItem.DoesNotExist:
            raise ValidationError({'sale_item': 'Sale item does not exist'})


class SaleItem(models.Model):
    """
    A SaleItem represents the individual line items for a single sale.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sale = models.ForeignKey(
        Sale, related_name="sale_items", on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, related_name="sale_items", on_delete=models.SET(get_deleted_product))
    quantity = models.IntegerField()
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2, editable=False)
    deleted_product_name = models.CharField(
        max_length=255, null=True, blank=True, editable=False)

    @property
    def subtotal(self):
        return self.quantity * self.unit_price

    def save(self, *args, **kwargs):
        if not self.product.product_name == "DELETED":
            self.unit_price = self.product.selling_price
        return super().save(*args, **kwargs)

    def clean(self):
        # Check if product quantity is sufficient
        if self.quantity > self.product.quantity_in_stock:
            raise ValidationError({'quantity': f'Sale item quantity cannot exceed product quantity ({
                                  self.product.quantity_in_stock})'})
        super().clean()


@receiver(pre_delete, sender=Product)
def update_saleitem_deleted_product_name(sender, instance, **kwargs):
    sale_items = SaleItem.objects.filter(product=instance)
    for sale_item in sale_items:
        # Assuming 'name' is a field in the Product model
        sale_item.deleted_product_name = instance.name
        sale_item.save()

# setting up this also for push
