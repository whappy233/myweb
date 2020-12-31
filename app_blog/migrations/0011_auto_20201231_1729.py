# Generated by Django 2.2 on 2020-12-31 17:29

import ckeditor_uploader.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app_blog', '0010_auto_20201230_1622'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='users_like',
            field=models.ManyToManyField(blank=True, related_name='blog_liked', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='post',
            name='body',
            field=ckeditor_uploader.fields.RichTextUploadingField(verbose_name='正文'),
        ),
    ]
