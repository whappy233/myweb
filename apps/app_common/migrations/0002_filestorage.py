# Generated by Django 2.2 on 2021-06-15 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_common', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FileStorage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='文件名')),
                ('file', models.FileField(blank=True, upload_to='uploads/', verbose_name='文件')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='上传日期')),
            ],
            options={
                'verbose_name': '文件存储',
                'verbose_name_plural': '文件存储',
                'ordering': ['created'],
            },
        ),
    ]
