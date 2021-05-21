# Generated by Django 2.2 on 2021-05-15 08:11

from django.db import migrations, models
import django.db.models.deletion
import imagekit.models.fields
import myweb.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Gallery',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(blank=True)),
                ('title', models.TextField(max_length=1024, verbose_name='相册名称')),
                ('is_visible', models.BooleanField(default=True, verbose_name='是否可见')),
                ('mod_date', models.DateTimeField(auto_now=True, verbose_name='更新日期')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='创建日期')),
                ('thumb', imagekit.models.fields.ProcessedImageField(upload_to='albums', verbose_name='缩略图')),
                ('is_delete', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': '相册',
                'verbose_name_plural': '相册',
                'ordering': ('-mod_date',),
            },
            bases=(models.Model, myweb.utils.AdminMixin),
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', imagekit.models.fields.ProcessedImageField(upload_to='photo')),
                ('thumb', imagekit.models.fields.ProcessedImageField(blank=True, null=True, upload_to='photo/thumbs/', verbose_name='缩略图')),
                ('alt', models.CharField(blank=True, default='', max_length=255, verbose_name='描述')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='创建日期')),
                ('is_delete', models.BooleanField(default=False)),
                ('gallery', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='photos', to='app_gallery.Gallery', verbose_name='所属相册')),
            ],
            options={
                'verbose_name': '相片',
                'verbose_name_plural': '相片',
                'ordering': ('-create_date',),
            },
            bases=(models.Model, myweb.utils.AdminMixin),
        ),
    ]
