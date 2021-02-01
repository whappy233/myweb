import base64

from ckeditor_uploader.fields import RichTextUploadingField  # 富文本编辑器 ckeditor
from mdeditor.fields import MDTextField  # 富文本编辑器 mdeditor

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation

from django.db import models
from django.urls import reverse
from django.utils import timezone
from taggit.managers import TaggableManager  # 第三方标签应用

from .cn_taggit import CnTaggedItem
from myweb.utils import cache_decorator, cache
from uuid import uuid4
from app_comments.models import Comments

from loguru import logger


# 自定义的管理器
class PublishedManage(models.Manager):
    def get_queryset(self):
        # 修改管理器的初始 QuerySet
        # 状态为发布且发布时间小于现在的blog
        return super(PublishedManage, self).get_queryset().filter(pub_time__lte=timezone.now(), status='p')


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
        'self', verbose_name="父级分类", blank=True, null=True, on_delete=models.CASCADE, related_name='child_category')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('app_blog:category_detail', args=[self.slug])

    # 判断是否有子类别
    def has_child(self):
        # 反向查询
        if self.child_category.all().count() > 0:
            return True
        return False

    @cache_decorator(60 * 60 * 10)
    def get_category_tree(self):
        """递归获得分类目录的父级"""
        categorys = []
        def parse(category):
            categorys.append(category)
            if category.parent_category:
                return parse(category.parent_category)
        parse(self)
        return categorys

    @cache_decorator(60 * 60 * 10)
    def get_sub_categorys(self):
        """获得当前分类目录所有子集"""
        categorys = []
        all_categorys = Category.objects.all()
        def parse(category):
            if category not in categorys:
                categorys.append(category)
            childs = all_categorys.filter(parent_category=category)
            for child in childs:
                if category not in categorys:
                    categorys.append(child)
                return parse(child)
        parse(self)
        return categorys


    @staticmethod
    def xx():
        def parse(category):
            childs = Category.objects.filter(parent_category=category)
            for child in childs:
                if not child.has_child():
                    print({category.id:child.id})
                else:
                    return parse(child)

        top = Category.objects.filter(parent_category=None)
        for i in top:
            print(i.id)
            parse(i)



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
    COMMENT_STATUS = (('o', '打开'), ('c', '关闭'),)
    tags = TaggableManager(blank=True, through=CnTaggedItem)  # 添加标签管理器
    title = models.CharField('标题', max_length=250)
    # slug 字段用于 URL 中，仅包含字母数字下划线以及连字符。根据 slug 字段，可对博客构建具有良好外观和 SEO 友好的 URL。
    # 使用 unique_for_date 参数可采用发布日期与 slug 对帖子构建URL
    slug = models.SlugField('slug', max_length=250, unique_for_date='pub_time', blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_articles', verbose_name='作者')
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='blog_articles', verbose_name='分类', blank=False, null=False)
    users_like = models.ManyToManyField(User, related_name='blog_liked', blank=True)

    # body = RichTextUploadingField('正文')
    body = MDTextField('正文')
    views = models.PositiveIntegerField('阅读次数', default=0)
    pub_time = models.DateTimeField('发布时间', default=timezone.now, null=True, blank=True)
    created = models.DateTimeField('创建时间', auto_now_add=True)
    updated = models.DateTimeField('更新时间', auto_now=True)
    status = models.CharField('文章状态', max_length=10, choices=STATUS_CHOICES, default='d')
    is_delete = models.BooleanField('是否逻辑删除', default=False)

    comment_status = models.CharField('评论状态', max_length=1, choices=COMMENT_STATUS, default='o')
    article_order = models.IntegerField('排序,数字越大越靠前', blank=False, null=False, default=0)

    # contenttypes
    comments = GenericRelation(Comments)  # 该字段不会存储于数据库中(用于反向关系查询)

    objects = models.Manager()  # 默认管理器
    # objects = aaa()   # 在默认管理器上增加了方法
    published = PublishedManage()  # 自定义的管理器应在默认管理器的后面
    # from django.contrib.auth.models import User
    # from app_blog.models import Article
    # Article.published.filter(title__startswith='w')

    class Meta:
        ordering = ('-pub_time',)  # 出版日期降序
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
        self.pub_time = timezone.now()
        self.save(update_fields=['status', 'pub_time'])

    def to_draft(self):
        self.status = 'd'
        self.pub_time = None
        self.save(update_fields=['status', 'pub_time'])

    # 标准 urls
    def get_absolute_url(self):  # 构建URL
        # <int:year>/<int:month>/<int:day>/<slug:slug>/self.id/
        # /2020/1/10/markdown/3
        a = [self.pub_time.year, self.pub_time.month, self.pub_time.day, self.slug, self.id]
        return reverse('app_blog:article_detail', args=a)

    def get_admin_url(self):
        '''获取 admin 的文章编辑界面'''
        info = (self._meta.app_label, self._meta.model_name)
        return reverse('admin:%s_%s_change' % info, args=(self.pk,))

    def comment_list(self):
        '''获取对应文章的所有评论'''
        cache_key = f'article_comments_{self.id}'
        value = cache.get(cache_key)
        if value:
            logger.info(f'获取评论缓存:{cache_key}')
            return value
        else:
            comments = self.comments.filter(is_active=True)  # 查询所有评论
            cache.set(cache_key, comments, 60 * 100)
            logger.info(f'设置评论缓存:{cache_key}')
            return comments

    @cache_decorator(60 * 60 * 10)
    def get_category_tree(self):
        tree = self.category.get_category_tree()
        names = list(map(lambda c: (c.name, c.get_absolute_url()), tree))
        return names



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
    # 草稿文章(d)不应该有发布日期( pub_time )
    # 当文章状态为发布(p), 而发布日期为空时，发布日期应该为当前时间
    def clean(self):
        # 不允许草稿条目具有 pub_time
        if self.status == 'd' and self.pub_time is not None:
            self.pub_time = None
            # raise ValidationError('草稿没有发布日期. 发布日期已清空。')
        if self.status == 'p' and self.pub_time is None:
            self.pub_time = timezone.now()


