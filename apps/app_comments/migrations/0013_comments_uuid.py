# Generated by Django 2.2 on 2021-05-19 15:25

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('app_comments', '0012_auto_20210518_2048'),
    ]

    operations = [
        migrations.AddField(
            model_name='comments',
            name='uuid',
            field=models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, unique=True, verbose_name='唯一标识'),
        ),
    ]