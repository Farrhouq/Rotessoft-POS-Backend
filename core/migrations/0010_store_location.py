# Generated by Django 5.1.1 on 2024-10-15 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_alter_sale_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='location',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
