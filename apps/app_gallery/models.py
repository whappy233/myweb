from django.db import models
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit
from django.urls import reverse
from django.utils.text import slugify
from random import choice
from myweb.utils import AdminMixin
from django.db.models import Count

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


# 自定义的管理器
class GalleryNotNullManager(models.Manager):
    '''不为空的相册'''
    def get_queryset(self):
        return super(GalleryNotNullManager, self).get_queryset().\
        annotate(photo_num=Count('photos')).filter(photo_num__gt=0)




# 相册
class Gallery(models.Model, AdminMixin):
    slug = models.SlugField(max_length=50, blank=True)
    title = models.TextField(max_length=1024, verbose_name='相册名称')
    is_visible = models.BooleanField(default=True, verbose_name='是否可见')
    mod_date = models.DateTimeField(auto_now=True, verbose_name='更新日期')
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='创建日期')
    # 图片上传文件夹(/albums/)
    thumb = ProcessedImageField(upload_to='albums', processors=[ResizeToFit(300, 300, mat_color=(255, 255, 255))],
                                format='JPEG', options={'quality': 100}, verbose_name='缩略图')
    is_delete = models.BooleanField(default=False)

    objects = models.Manager()  # 默认管理器
    notNull = GalleryNotNullManager()  # 自定义的管理器应在默认管理器的后面


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
    # 缩略图目的文件夹((/albums/thumb/)
    thumb = ProcessedImageField(upload_to='photo/thumbs/', processors=[ResizeToFit(300)], format='JPEG',
                                options={'quality': 80}, blank=True, null=True, verbose_name='缩略图')
    alt = models.CharField(max_length=255, default='',
                           blank=True, verbose_name='描述')
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='创建日期')
    is_delete = models.BooleanField(default=False)

    objects = PhotoManager()  # 自定义的管理器应在默认管理器的后面

    class Meta:
        verbose_name = '相片'
        verbose_name_plural = verbose_name
        ordering = ('-create_date',)

    def __str__(self):
        return self.alt
