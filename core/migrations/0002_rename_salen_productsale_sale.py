# Generated by Django 5.1.1 on 2024-11-09 09:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='productsale',
            old_name='salen',
            new_name='sale',
        ),
    ]
