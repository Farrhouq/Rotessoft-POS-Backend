# Generated by Django 5.1.1 on 2024-10-10 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='adminuserprofile',
            name='phone',
        ),
        migrations.RemoveField(
            model_name='adminuserprofile',
            name='updated_at',
        ),
        migrations.RemoveField(
            model_name='staffuserprofile',
            name='phone',
        ),
        migrations.AlterField(
            model_name='adminuserprofile',
            name='address',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='staffuserprofile',
            name='address',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, unique=True),
        ),
    ]