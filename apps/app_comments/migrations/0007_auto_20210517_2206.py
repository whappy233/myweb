# Generated by Django 2.2 on 2021-05-17 22:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_comments', '0006_auto_20210517_2203'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wanderer',
            name='email',
            field=models.EmailField(max_length=30, unique=True, verbose_name='邮箱'),
        ),
    ]
