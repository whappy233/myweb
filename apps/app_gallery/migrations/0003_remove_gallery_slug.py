# Generated by Django 2.2 on 2021-06-01 17:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_gallery', '0002_auto_20210601_1704'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gallery',
            name='slug',
        ),
    ]
