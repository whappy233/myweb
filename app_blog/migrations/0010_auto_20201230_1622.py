# Generated by Django 2.2 on 2020-12-30 16:22

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('app_blog', '0009_auto_20201230_1619'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='publish',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True, verbose_name='发布时间'),
        ),
    ]
