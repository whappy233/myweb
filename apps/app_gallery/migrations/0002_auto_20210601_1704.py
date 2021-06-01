# Generated by Django 2.2 on 2021-06-01 17:04

import app_common.models
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('app_gallery', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='gallery',
            options={'ordering': ('-last_mod_time',), 'verbose_name': '相册', 'verbose_name_plural': '相册'},
        ),
        migrations.RemoveField(
            model_name='gallery',
            name='create_date',
        ),
        migrations.RemoveField(
            model_name='gallery',
            name='mod_date',
        ),
        migrations.AddField(
            model_name='gallery',
            name='created_time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='创建时间'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='gallery',
            name='last_mod_time',
            field=models.DateTimeField(auto_now=True, verbose_name='修改时间'),
        ),
        migrations.AddField(
            model_name='gallery',
            name='uuid',
            field=models.CharField(default=app_common.models.uuid4_hex, editable=False, max_length=10, unique=True, verbose_name='唯一标识'),
        ),
        migrations.AlterField(
            model_name='gallery',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
