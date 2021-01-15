import base64

from ckeditor_uploader.fields import RichTextUploadingField  # 富文本编辑器
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import (GenericForeignKey,
                                                GenericRelation)

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from django.utils import timezone
from taggit.managers import TaggableManager  # 第三方标签应用

from .cn_taggit import CnTaggedItem

from uuid import uuid4

# 自定义的管理器
class PublishedManage(models.Manager):
    def get_queryset(self):
        # 修改管理器的初始 QuerySet
        # 状态为发布且发布时间小于现在的blog
        return super(PublishedManage, self).get_queryset().filter(publish__lte=timezone.now(), status='p')

# 在默认管理器上增加方法
class aaa(models.Manager):
    def get_status(self):
        try:
            a = self.get(status='p')
        except:
            a = None
        return  a

# 文章分类
class Category(models.Model):
    """文章分类"""
    name = models.CharField('分类名', max_length=30, unique=True)
    slug = models.SlugField('slug', max_length=40, blank=True)
    # category.parent_category  判断是否有父类别
    parent_category = models.ForeignKey(  # 自关联
        'self', verbose_name="父级分类", blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:category_detail', args=[self.slug])

    # 判断是否有子类别
    def has_child(self):
        if self.category_set.all().count() > 0:
            return True

    class Meta:
        ordering = ['name']
        verbose_name = "分类"
        verbose_name_plural = verbose_name

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = base64.urlsafe_b64encode(
                self.name.encode()).decode().rstrip('=')
            # print(base64.urlsafe_b64decode(
            #     slug + '=' * (4 - len(slug) % 4)).decode())  # 解码
            self.slug = slug
        super().save(*args, **kwargs)

# 文章模型
class Article(models.Model):
    '''文章模型'''
    STATUS_CHOICES = (('d', '草稿'), ('p', '发布'),)
    tags = TaggableManager(blank=True, through=CnTaggedItem)  # 添加标签管理器
    title = models.CharField('标题', max_length=250)
    # slug 字段用于 URL 中，仅包含字母数字下划线以及连字符。根据 slug 字段，可对博客构建具有良好外观和 SEO 友好的 URL。
    # 使用 unique_for_date 参数可采用发布日期与 slug 对帖子构建URL
    slug = models.SlugField('slug', max_length=250, unique_for_date='publish', blank=True)
    # related_name 指定反向关系名称(从User到Article)
    users_like = models.ManyToManyField(User, related_name='blog_liked', blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_articles', verbose_name='作者')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='blog_articles', verbose_name='分类', blank=False, null=False)

    body = RichTextUploadingField('正文')
    views = models.PositiveIntegerField('阅读次数', default=0)
    publish = models.DateTimeField('发布时间', default=timezone.now, null=True, blank=True)
    created = models.DateTimeField('创建时间', auto_now_add=True)
    updated = models.DateTimeField('更新时间', auto_now=True)
    status = models.CharField('文章状态', max_length=10, choices=STATUS_CHOICES, default='d')
    is_delete = models.BooleanField('是否不可见', default=False)

    # contenttypes
    comments = GenericRelation('Comment')  # 该字段不会存储于数据库中(用于反向关系查询)

    objects = models.Manager()  # 默认管理器
    # objects = aaa()   # 在默认管理器上增加了方法
    published = PublishedManage()  # 自定义的管理器应在默认管理器的后面
    # from django.contrib.auth.models import User
    # from app_blog.models import Article
    # Article.published.filter(title__startswith='w')

    class Meta:
        ordering = ('-publish',)  # 出版日期降序
        verbose_name = '文章'  # 定义一个可读名字
        verbose_name_plural = verbose_name
        # Django项目中如果你需要频繁地对数据表中的某些字段(如title)使用filter(), exclude()和order_by()方法进行查询，
        # 建议你对这些字段建议索引(index), 提升查询效率
        indexes = [
            models.Index(fields=['title']),  # 建立索引
        ]

    def __str__(self):
        return self.title

    def viewed(self):
        self.views += 1
        # 只需要更新views的字段，而不是更新全表，减轻数据库写入的工作量
        self.save(update_fields=['views'])

    def to_publish(self):
        self.status = 'p'
        self.publish = timezone.now()
        self.save(update_fields=['status', 'publish'])

    def to_draft(self):
        self.status = 'd'
        self.publish = None
        self.save(update_fields=['status', 'publish'])

    # 标准 urls
    def get_absolute_url(self):  # 构建URL
        # <int:year>/<int:month>/<int:day>/<slug:slug>/
        # /2020/1/10/markdown/
        a = [self.publish.year, self.publish.month, self.publish.day, self.slug]
        return reverse('app_blog:article_detail', args=a)

    # 重写save方法
    def save(self, *args, **kwargs):
        if not self.slug:
            # slug = base64.urlsafe_b64encode(self.title.encode()).decode().rstrip('=')
            # print(base64.urlsafe_b64decode(
            #     slug + '=' * (4 - len(slug) % 4)).decode())  # 解码
            slug = uuid4().hex[:10]
            self.slug = slug
        super().save(*args, **kwargs)

    # save 前的验证
    # 草稿文章(d)不应该有发布日期( publish )
    # 当文章状态为发布(p), 而发布日期为空时，发布日期应该为当前时间
    def clean(self):
        # 不允许草稿条目具有 publish
        if self.status == 'd' and self.publish is not None:
            self.publish = None
            # raise ValidationError('草稿没有发布日期. 发布日期已清空。')
        if self.status == 'p' and self.publish is None:
            self.publish = timezone.now()


# 评论模型
class Comment(models.Model):
    '''评论模型'''
    name = models.CharField(max_length=80, verbose_name='名字')
    email = models.EmailField(verbose_name='邮箱', blank=True)
    body = models.TextField(verbose_name='评论')
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    active = models.BooleanField(default=True, verbose_name='是否有效')  # 隐式删除

    content_type = models.ForeignKey(ContentType, on_delete=None, verbose_name='内容类型')   # step1 内容类型，代表了模型的名字(比如Article, Picture)
    object_id = models.PositiveIntegerField('关联对象的ID')                       # step2 传入对象的id
    content_object = GenericForeignKey('content_type', 'object_id') # step3 传入的实例化对象，其包含两个属性content_type和object_id

    class Meta:
        ordering = ('created',)
        verbose_name = '评论'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'(关联的模型: {self.content_type}, 对应ID: {self.object_id})'
