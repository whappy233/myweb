# Generated by Django 3.0.7 on 2020-12-15 14:11

import app_user.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_user', '0002_auto_20201212_1618'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='photo',
            field=models.ImageField(blank=True, upload_to=app_user.models.user_directory_path, verbose_name='头像'),
        ),
    ]