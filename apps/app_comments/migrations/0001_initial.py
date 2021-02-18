# Generated by Django 2.2 on 2021-01-28 08:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Comments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField(verbose_name='正文')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否显示')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('last_mod_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='修改时间')),
                ('object_id', models.PositiveIntegerField(verbose_name='关联对象ID')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='作者')),
                ('content_type', models.ForeignKey(limit_choices_to={'model__in': ('article',)}, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType', verbose_name='关联对象类型')),
                ('parent_comment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app_comments.Comments', verbose_name='上级评论')),
            ],
            options={
                'verbose_name': '评论',
                'verbose_name_plural': '评论',
                'ordering': ('last_mod_time',),
            },
        ),
    ]