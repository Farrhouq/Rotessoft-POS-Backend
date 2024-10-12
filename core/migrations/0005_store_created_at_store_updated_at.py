# Generated by Django 5.1.1 on 2024-10-11 11:09

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_store_admin'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='store',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
