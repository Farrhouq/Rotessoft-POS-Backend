# Generated by Django 5.1.1 on 2024-10-14 10:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_store_daily_target_alter_product_unique_together'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sale',
            options={'ordering': ['-created_at']},
        ),
    ]