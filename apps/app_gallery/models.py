from django.db import models
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit
from django.urls import reverse
from django.utils.text import slugify
from random import choice
from myweb.utils import AdminMixin
from django.db.models import Count
from django.contrib.contenttypes.fields import GenericRelation
from app_comments.models import Comments



# 默认 Photo 管理器增加方法
class PhotoManager(models.Manager):
    def get_random_photo(self, total: int = 1):
        '''随机获取一张图片'''
        count = self.count()
        if count > 0:
            all_photos = self.all()
            if total == 1:
                return choice(all_photos)
            return [choice(all_photos) for _ in range(total)]
        return []


# 自定义 Gallery 管理器
class GalleryNotNullManager(models.Manager):
    '''不为空的相册'''

    def get_queryset(self):
        return super(GalleryNotNullManager, self).get_queryset().\
            annotate(photo_num=Count('photos')).filter(photo_num__gt=0)


# 相册
class Gallery(models.Model, AdminMixin):
    slug = models.SlugField(max_length=50, blank=True)
    title = models.CharField('相册名称', max_length=100)
    is_visible = models.BooleanField('是否可见', default=True)
    mod_date = models.DateTimeField('更新日期', auto_now=True)
    create_date = models.DateTimeField('创建日期', auto_now_add=True)
    is_delete = models.BooleanField('已删除', default=False)
    # 图片上传文件夹(media/albums/)
    thumb = ProcessedImageField(upload_to='albums', processors=[ResizeToFit(300)], format='JPEG', options={'quality': 100}, verbose_name='缩略图')

    # contenttypes
    comments = GenericRelation(Comments)  # 该字段不会存储于数据库中(用于反向关系查询)


    # 默认管理器
    objects = models.Manager()
    # 自定义的管理器应在默认管理器的后面
    notNull = GalleryNotNullManager()

    def __str__(self):
        return self.title

    def get_some_photo(self, total=1):
        return self.photos.get_random_photo(total)

    class Meta:
        verbose_name = '相册'
        ordering = ('-mod_date',)
        verbose_name_plural = verbose_name

    def get_absolute_url(self):
        return reverse('app_gallery:photo_detail', kwargs={'pk': self.pk, 'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = slugify(self.title, True)[:8]
            self.slug = slug
        super().save(*args, **kwargs)


# 一张相片
class Photo(models.Model, AdminMixin):
    gallery = models.ForeignKey(Gallery, on_delete=models.PROTECT, related_name='photos', verbose_name='所属相册')

    image = ProcessedImageField(upload_to='photo', processors=[ResizeToFit(1280)], format='JPEG', options={'quality': 70})
    # 缩略图目的文件夹(media/photo/thumb/)
    thumb = ProcessedImageField(upload_to='photo/thumbs/', processors=[ResizeToFit(300)], format='JPEG', options={'quality': 80}, blank=True, null=True, verbose_name='缩略图')
    title = models.CharField('标题', max_length=255, default='', blank=True)
    create_date = models.DateTimeField('创建日期', auto_now_add=True)
    is_delete = models.BooleanField('已删除', default=False)

    objects = PhotoManager()

    class Meta:
        verbose_name = '相片'
        verbose_name_plural = verbose_name
        ordering = ('-create_date',)

    def __str__(self):
        return self.title
