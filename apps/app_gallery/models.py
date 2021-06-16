from django.db import models
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit
from django.urls import reverse
from django.utils.text import slugify
from random import choice
from myweb.utils import AdminMixin
from django.db.models import Count
from django.contrib.contenttypes.fields import GenericRelation

import os

from app_comments.models import Comments
from app_common.models import BaseModel


class PhotoManager(models.Manager):
    def get_random_photo(self, total: int = 1):
        '''随机获取一张图片'''
        count = self.count()
        if count > 0:
            all_photos = self.filter(is_delete=False)
            if total == 1:
                return choice(all_photos)
            return [choice(all_photos) for _ in range(total)]
        return []


class GalleryNotNullManager(models.Manager):
    '''不为空的相册'''

    def get_queryset(self):
        return super(GalleryNotNullManager, self).get_queryset().\
            annotate(photo_num=Count('photos')).filter(photo_num__gt=0)


# gallery/{gallery_title}/{thumb_name}
def gallery_directory_path(instance, filename):
    ext = os.path.splitext(filename)[-1]
    gallery_title = instance.title
    newname = gallery_title + ext
    return os.path.join('gallery', gallery_title, newname)


class Gallery(BaseModel, AdminMixin):
    '''相册'''

    title = models.CharField('相册名称', max_length=100, unique=True)
    # 图片上传文件夹(media/gallery/)
    thumb = ProcessedImageField(processors=[ResizeToFit(300)],
                                format='JPEG',
                                options={'quality': 100},
                                verbose_name='缩略图',
                                upload_to=gallery_directory_path)

    is_delete = models.BooleanField('已删除', default=False)
    is_visible = models.BooleanField('是否可见', default=True)

    # contenttypes
    comments = GenericRelation(Comments)  # 该字段不会存储于数据库中(用于反向关系查询)

    objects = models.Manager()  # 默认管理器
    nonEmpty = GalleryNotNullManager()

    def __str__(self):
        return self.title

    def get_some_photo(self, total=1):
        return self.photos.get_random_photo(total)

    def get_absolute_url(self):
        return reverse('app_gallery:gallery_detail', args=(self.uuid,))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = '相册'
        ordering = ('-last_mod_time',)
        verbose_name_plural = verbose_name


# gallery/{gallery_title}/photo/{image_name}
def photo_directory_path(instance, filename):
    gallery_title = instance.gallery
    return os.path.join('gallery', str(gallery_title), 'photo', filename)

# gallery/{gallery_title}/thumb/thumb-{image_name}
def thumb_directory_path(instance, filename):
    gallery_title = instance.gallery
    return os.path.join('gallery', str(gallery_title), 'thumb', filename)


# 一张相片
class Photo(models.Model, AdminMixin):
    gallery = models.ForeignKey(Gallery,
                                on_delete=models.PROTECT,
                                related_name='photos',
                                verbose_name='所属相册')

    # image = ProcessedImageField(processors=[ResizeToFit(1280)], ormat='JPEG', options={'quality': 1000}, upload_to='photo')

    # image.url  # 图像URL地址
    image = models.ImageField('图片', upload_to=photo_directory_path)

    # 缩略图目的文件夹(media/photo/thumb/)
    thumb = ProcessedImageField(processors=[ResizeToFit(300)],
                                format='JPEG',
                                options={'quality': 80},
                                blank=True, null=True,
                                verbose_name='缩略图', upload_to=thumb_directory_path)

    title = models.CharField('标题', max_length=255, default='', blank=True)
    description = models.TextField('描述', default='', blank=True)
    create_date = models.DateTimeField('创建日期', auto_now_add=True)
    is_delete = models.BooleanField('已删除', default=False)

    objects = PhotoManager()

    class Meta:
        verbose_name = '相片'
        verbose_name_plural = verbose_name
        ordering = ('-create_date',)

    def __str__(self):
        return self.title
