# Generated by Django 2.2 on 2021-01-18 17:13

import ckeditor_uploader.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
        ('taggit', '0003_taggeditem_add_unique_index'),
    ]

    operations = [
        migrations.CreateModel(
            name='CnTag',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('taggit.tag',),
        ),
        migrations.CreateModel(
            name='CnTaggedItem',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('taggit.taggeditem',),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80, verbose_name='名字')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='邮箱')),
                ('body', models.TextField(verbose_name='评论')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('active', models.BooleanField(default=True, verbose_name='是否有效')),
                ('object_id', models.PositiveIntegerField(verbose_name='关联对象的ID')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType', verbose_name='内容类型')),
            ],
            options={
                'verbose_name': '评论',
                'verbose_name_plural': '评论',
                'ordering': ('created',),
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True, verbose_name='分类名')),
                ('slug', models.SlugField(blank=True, max_length=40, verbose_name='slug')),
                ('parent_category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app_blog.Category', verbose_name='父级分类')),
            ],
            options={
                'verbose_name': '分类',
                'verbose_name_plural': '分类',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250, verbose_name='标题')),
                ('slug', models.SlugField(blank=True, max_length=250, unique_for_date='publish', verbose_name='slug')),
                ('body', ckeditor_uploader.fields.RichTextUploadingField(verbose_name='正文')),
                ('views', models.PositiveIntegerField(default=0, verbose_name='阅读次数')),
                ('publish', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True, verbose_name='发布时间')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('status', models.CharField(choices=[('d', '草稿'), ('p', '发布')], default='d', max_length=10, verbose_name='文章状态')),
                ('is_delete', models.BooleanField(default=False, verbose_name='是否逻辑删除')),
                ('comment_status', models.CharField(choices=[('o', '打开'), ('c', '关闭')], default='o', max_length=1, verbose_name='评论状态')),
                ('article_order', models.IntegerField(default=0, verbose_name='排序,数字越大越靠前')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blog_articles', to=settings.AUTH_USER_MODEL, verbose_name='作者')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blog_articles', to='app_blog.Category', verbose_name='分类')),
                ('tags', taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='app_blog.CnTaggedItem', to='taggit.Tag', verbose_name='Tags')),
                ('users_like', models.ManyToManyField(blank=True, related_name='blog_liked', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '文章',
                'verbose_name_plural': '文章',
                'ordering': ('-publish',),
            },
        ),
        migrations.AddIndex(
            model_name='article',
            index=models.Index(fields=['title'], name='app_blog_ar_title_71b6f0_idx'),
        ),
    ]
