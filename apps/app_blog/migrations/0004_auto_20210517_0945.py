# Generated by Django 2.2 on 2021-05-17 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_blog', '0003_auto_20210516_1426'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='is_delete',
            field=models.BooleanField(default=False, verbose_name='已删除'),
        ),
    ]
