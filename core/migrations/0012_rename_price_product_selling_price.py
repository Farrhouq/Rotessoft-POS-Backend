# Generated by Django 5.1.1 on 2024-10-16 23:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_alter_store_daily_target'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='price',
            new_name='selling_price',
        ),
    ]
