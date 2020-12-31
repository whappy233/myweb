# Generated by Django 2.2 on 2020-12-23 10:05

from django.db import migrations, models
import django.db.models.deletion
import imagekit.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('app_gallery', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='gallery',
            options={'ordering': ('mod_date',), 'verbose_name': '相册', 'verbose_name_plural': '相册'},
        ),
        migrations.AlterModelOptions(
            name='photo',
            options={'verbose_name': '相片', 'verbose_name_plural': '相片'},
        ),
        migrations.AddField(
            model_name='gallery',
            name='is_delete',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='photo',
            name='is_delete',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='gallery',
            name='create_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='创建日期'),
        ),
        migrations.AlterField(
            model_name='gallery',
            name='is_visible',
            field=models.BooleanField(default=True, verbose_name='是否可见'),
        ),
        migrations.AlterField(
            model_name='gallery',
            name='mod_date',
            field=models.DateTimeField(auto_now=True, verbose_name='更新日期'),
        ),
        migrations.AlterField(
            model_name='gallery',
            name='thumb',
            field=imagekit.models.fields.ProcessedImageField(upload_to='albums', verbose_name='缩略图'),
        ),
        migrations.AlterField(
            model_name='gallery',
            name='title',
            field=models.TextField(max_length=1024, verbose_name='相册名称'),
        ),
        migrations.AlterField(
            model_name='photo',
            name='alt',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='描述'),
        ),
        migrations.AlterField(
            model_name='photo',
            name='create_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='创建日期'),
        ),
        migrations.AlterField(
            model_name='photo',
            name='gallery',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='photos', to='app_gallery.Gallery', verbose_name='所属相册'),
        ),
        migrations.AlterField(
            model_name='photo',
            name='thumb',
            field=imagekit.models.fields.ProcessedImageField(blank=True, null=True, upload_to='photo/thumbs/', verbose_name='缩略图'),
        ),
    ]