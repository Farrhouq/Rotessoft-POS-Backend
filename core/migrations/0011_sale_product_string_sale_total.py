# Generated by Django 5.1.1 on 2024-11-09 17:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_alter_sale_sale_made_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='product_string',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='sale',
            name='total',
            field=models.FloatField(null=True),
        ),
    ]