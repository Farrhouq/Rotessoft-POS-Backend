# Generated by Django 5.1.1 on 2024-10-16 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_store_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='daily_target',
            field=models.FloatField(default=1000),
        ),
    ]
