from abc import abstractmethod
from django.db import models

from django.core.exceptions import ValidationError
from django.db.models import fields
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from myweb.utils import get_current_site
from django.core.cache import cache
from rest_framework import serializers
import re
import os

from uuid import uuid4

def uuid4_hex():
    return uuid4().hex[:10]

def file_path(instance, filename):
    ext = os.path.splitext(filename)[-1]
    newname = uuid4().hex + ext
    return os.path.join('uploads', now().strftime('%Y/%m/%d/'), newname)



class FileStorage(models.Model):
    name = models.CharField('文件名', max_length=50, blank=True, null=True)
    file = models.FileField('文件', upload_to=file_path)
    size = models.CharField('文件大小', max_length=32, blank=True, null=True, editable=False)
    created = models.DateTimeField('上传日期', auto_now_add=True)
    is_delete = models.BooleanField('已删除', default=False)

    class Meta:
        verbose_name = '文件存储'
        verbose_name_plural = verbose_name
        ordering = ['created']

    def __str__(self) -> str:
        name = self.name or os.path.basename(self.file.name)
        return f'{name}[size: {self.size}]'

class FileSerializers(serializers.ModelSerializer):

    class Meta:
        model = FileStorage
        fields = '__all__'
        read_only_fields = ['name', 'size', 'created', 'is_delete']




class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.CharField('唯一标识', max_length=10, unique=True, default=uuid4_hex, editable=False)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_mod_time = models.DateTimeField('修改时间', auto_now=True)

    def get_full_url(self):
        site = get_current_site().domain
        url = f"https://{site}{self.get_absolute_url()}"
        return url

    class Meta:
        abstract = True

    @abstractmethod
    def get_absolute_url(self):
        pass



class BlogSettings(models.Model):
    '''站点设置 '''
    sitename = models.CharField("网站名称", max_length=200, null=False, blank=False, default='')
    site_description = models.TextField("网站描述", max_length=1000, null=False, blank=False, default='')
    site_seo_description = models.TextField("网站SEO描述", max_length=1000, null=False, blank=False, default='')
    site_keywords = models.TextField("网站关键字", max_length=1000, null=False, blank=False, default='')
    article_sub_length = models.IntegerField("文章摘要长度", default=100)
    sidebar_article_count = models.IntegerField("侧边栏文章数目", default=10)
    sidebar_comment_count = models.IntegerField("侧边栏评论数目", default=5)
    show_google_adsense = models.BooleanField('是否显示谷歌广告', default=False)
    allow_register = models.BooleanField('是否允许用户注册', default=False)
    google_adsense_codes = models.TextField('广告内容', max_length=2000, null=True, blank=True, default='')
    open_site_comment = models.BooleanField('是否打开网站评论功能', default=True)
    beiancode = models.CharField('备案号', max_length=2000, null=True, blank=True, default='')
    analyticscode = models.TextField("网站统计代码", max_length=1000, null=False, blank=True, default='')
    show_gongan_code = models.BooleanField('是否显示公安备案号', default=False, null=False)
    gongan_beiancode = models.TextField('公安备案号', max_length=2000, null=True, blank=True, default='')
    resource_path = models.CharField("静态文件保存地址", max_length=300, null=False, default='/var/www/resource/')

    class Meta:
        verbose_name = '网站配置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.sitename

    def clean(self):
        if BlogSettings.objects.exclude(id=self.id).count():
            raise ValidationError(_('只能有一个配置'))

    def save(self, *args, **kwargs):
        try:
            self.full_clean()  
            super().save(*args, **kwargs)
            cache.clear()
        except ValidationError as e:
            from django.core.exceptions import NON_FIELD_ERRORS
            print('验证没通过： %s' % e.message_dict[NON_FIELD_ERRORS])



# 轮播图
class Carousel(models.Model):
    # 轮播图大小 820*200
    number = models.IntegerField('编号', help_text='编号决定图片播放的顺序，图片不要多于5张')
    title = models.CharField('标题', max_length=20, blank=True, null=True, help_text='标题可以为空')
    content = models.CharField('描述', max_length=80)
    img_url = models.CharField('图片地址', max_length=200, help_text='建议图片大小820*200')
    url = models.CharField('跳转链接', max_length=200, default='#', help_text='图片跳转的超链接，默认#表示不跳转')

    class Meta:
        verbose_name = '轮播图'
        verbose_name_plural = verbose_name
        # 编号越小越靠前，添加的时间约晚约靠前
        ordering = ['number', '-id']

    def __str__(self):
        return self.content[:25]


# 死链
class Silian(models.Model):
    badurl = models.CharField('死链地址', max_length=200, help_text='注意：地址是以http开头的完整链接格式')
    remark = models.CharField('死链说明', max_length=50, blank=True, null=True)
    add_date = models.DateTimeField('提交日期', auto_now_add=True)

    class Meta:
        verbose_name = '死链'
        verbose_name_plural = verbose_name
        ordering = ['-add_date']

    def __str__(self):
        return self.badurl


# 友链
class FriendLink(models.Model):
    name = models.CharField('网站名称', max_length=50)
    description = models.CharField('网站描述', max_length=100, blank=True)
    link = models.URLField('友链地址', help_text='请填写http或https开头的完整形式地址')
    logo = models.URLField('网站LOGO', help_text='请填写http或https开头的完整形式地址', blank=True)
    create_date = models.DateTimeField('创建时间', auto_now_add=True)
    is_active = models.BooleanField('是否有效', default=True)
    is_show = models.BooleanField('是否首页展示', default=False)

    class Meta:
        verbose_name = '友情链接'
        verbose_name_plural = verbose_name
        ordering = ['create_date']

    def __str__(self):
        return self.name

    def get_home_url(self):
        '''提取友链的主页'''
        u = re.findall(r'(http|https://.*?)/.*?', self.link)
        home_url = u[0] if u else self.link
        return home_url

    def active_to_false(self):
        self.is_active = False
        self.save(update_fields=['is_active'])

    def show_to_false(self):
        self.is_show = True
        self.save(update_fields=['is_show'])


# 关于
class AboutBlog(models.Model):
    body = models.TextField(verbose_name='About 内容')
    create_date = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    update_date = models.DateTimeField(verbose_name='修改时间', auto_now=True)

    class Meta:
        verbose_name = 'About'
        verbose_name_plural = verbose_name

    def __str__(self):
        return 'About'


