# Generated by Django 5.1.1 on 2024-10-12 00:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_alter_user_email_alter_user_phone_number'),
        ('core', '0006_alter_product_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='staffuserprofile',
            name='store',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='core.store'),
            preserve_default=False,
        ),
    ]
