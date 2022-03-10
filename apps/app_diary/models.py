from django.db import models
from django.urls import reverse
from django.utils.timezone import now
from mdeditor.fields import MDTextField
from rest_framework import serializers

from myweb.utils import markdown_render


class Diary(models.Model):
    MOOD = (
        ('shy', '害羞🥰'),
        ('hehe', '呵呵🙂'),
        ('smug', '得意🤪'),
        ('happy', '高兴😆'), 
        ('anger', '愤怒😡'),
        ('lonely', '寂寞😶'),
        ('nervous', '紧张😅'),
        ('anxiety', '焦虑😞'),
        ('annoyed', '恼怒😤'),
        ('confused', '困惑🤯'),
        ('disgusted', '厌恶🤮'),
        ('embarassed', '尴尬🥴'),
        ('exhausted', '精疲力尽😵'),
    )

    body = MDTextField('正文', image_upload_folder='diary_images')
    slug = models.SlugField('slug', blank=True, unique=True)
    mood = models.CharField('心情', max_length=15, choices=MOOD, default='happy')
    created = models.DateTimeField('创建时间', auto_now_add=True)
    updated = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        ordering = ('-created',)
        verbose_name = '日记'
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        return f'{self.body[:10]}...'

    # 标准 urls
    def get_absolute_url(self):  # 构建URL
        # /diary/<slug:slug>/
        return reverse('app_diary:diary_detail', args=(self.slug,))

    def save(self, *args ,**kwargs):
        if not self.slug:
            self.slug = now().strftime('%Y%m%d%H%M%S_%f')
        return super().save(*args ,**kwargs)

    def body_to_markdown(self):
        content, _ = markdown_render(self.body, True)
        return content


class DiarySerializer(serializers.Serializer):

    body = serializers.CharField(read_only=True, source="body_to_markdown")
    mood = serializers.ChoiceField(read_only=True, choices=Diary.MOOD, default='happy')
    created = serializers.DateTimeField(read_only=True)


