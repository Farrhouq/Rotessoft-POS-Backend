# Generated by Django 5.1.1 on 2024-10-22 21:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_product_cost_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='amount_in_stock',
            field=models.PositiveIntegerField(),
        ),
    ]