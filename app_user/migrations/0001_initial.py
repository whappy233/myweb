# Generated by Django 3.0.7 on 2021-01-15 22:18

import app_user.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(blank=True, default='users/default.png', upload_to=app_user.models.user_directory_path, verbose_name='头像')),
                ('org', models.CharField(blank=True, max_length=128, verbose_name='组织')),
                ('telephone', models.CharField(blank=True, max_length=50, verbose_name='手机号')),
                ('mod_date', models.DateTimeField(auto_now=True, verbose_name='最近修改')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User Profile',
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredient', to='app_user.Recipe')),
            ],
        ),
        migrations.AddConstraint(
            model_name='userprofile',
            constraint=models.UniqueConstraint(fields=('telephone',), name='unique_phone'),
        ),
    ]
