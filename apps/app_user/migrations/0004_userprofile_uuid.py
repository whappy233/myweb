# Generated by Django 2.2 on 2021-05-25 23:30

import app_user.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_user', '0003_auto_20210525_2256'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='uuid',
            field=models.CharField(default=app_user.models.uuid4_hex, editable=False, max_length=32, unique=True, verbose_name='唯一标识'),
        ),
    ]
