# Generated by Django 2.2 on 2021-05-17 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_comments', '0003_auto_20210517_1136'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comments',
            name='is_visible',
            field=models.BooleanField(default=True, verbose_name='是否可见'),
        ),
    ]
