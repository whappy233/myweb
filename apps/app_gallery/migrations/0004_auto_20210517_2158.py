# Generated by Django 2.2 on 2021-05-17 21:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_gallery', '0003_auto_20210517_1644'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='title',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='标题'),
        ),
    ]
