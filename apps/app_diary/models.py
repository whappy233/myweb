from django.db import models
from django.urls import reverse
from django.utils.timezone import now
import os




class Diary(models.Model):
    _MOOD = (
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
    body = models.TextField('正文')
    img = models.ImageField('图片', upload_to='diary', blank=True)
    slug = models.SlugField('slug', blank=True, unique=True)
    mood = models.CharField('心情', max_length=15, choices=_MOOD, default='happy')
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