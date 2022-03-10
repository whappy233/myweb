import base64
from uuid import uuid4

from ckeditor_uploader.fields import RichTextUploadingField  # 富文本编辑器 ckeditor
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from loguru import logger
from mdeditor.fields import MDTextField  # 富文本编辑器 mdeditor
from taggit.managers import TaggableManager  # 第三方标签应用

from myweb.utils import AdminMixin, cache, cache_decorator, markdown_render
from .cn_taggit import CnTaggedItem
from app_comments.models import Comments

# 无论在自定义的 Manager 中添加了什么特性，都必须能够对 Manager 实例进行简单的复制:
# 也就是说, 以下代码必须有效:
# import copy
# manager = MyManager()
# my_copy = copy.copy(manager)
# Django 在某些查询期间对管理器对象进行浅拷贝；如果您的管理器无法被复制，那么这些查询将失败。
# 对于大多数的资源管理器来说，这不是问题。若你只是为 Manager 添加简单的方法，一般不会疏忽地把 Manager 变的不可拷贝。
# 但是，若重写了 Manager 对象用于控制对象状态的 __getattr__ 或其它私有方法，你需要确认你的修改不会影响 Manager 被复制。


# 自定义 Article 管理器. 在默认管理器上增加方法
class ModelManager(models.Manager):
    def contain_comments_obj(self):
        '''包含评论的文章'''
        return  self.all().annotate(c=models.Count('comments')).filter(c__gt=0)

class PublishedManager(ModelManager):
    def get_queryset(self):
        # 修改管理器的初始 QuerySet
        # 状态为发布且发布时间小于现在的blog
        return super(PublishedManager, self).get_queryset().filter(pub_time__lte=timezone.now(), status='p')



# 文章分类 Model
class Category(models.Model):
    """文章分类"""
    name = models.CharField('分类名', max_length=30, unique=True)
    slug = models.SlugField('slug', max_length=40, blank=True)
    # 自关联 category.parent_category  判断是否有父类别
    parent_category = models.ForeignKey('self', on_delete=models.CASCADE,
                                        related_name='child_category',
                                        blank=True, null=True,
                                        verbose_name="父级分类")

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
    def get_all_parents(self):
        """获取所有父级"""
        categorys = []
        def parse(c):
            categorys.append(c)
            if c.parent_category:
                return parse(c.parent_category)
        parse(self)
        return categorys

    @cache_decorator(60 * 60 * 10)
    def get_all_children(self):
        """获取所有子级"""
        categorys = []
        all_categorys = Category.objects.all()
        def parse(c):
            if c not in categorys:
                categorys.append(c)
            childs = all_categorys.filter(parent_category=c)
            for child in childs:
                if c not in categorys:
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
        verbose_name = "文章分类"
        verbose_name_plural = verbose_name

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = base64.urlsafe_b64encode(
                self.name.encode()).decode().rstrip('=')
            # print(base64.urlsafe_b64decode(
            #     slug + '=' * (4 - len(slug) % 4)).decode())  # 解码
            self.slug = slug
        super().save(*args, **kwargs)


# 文章 Model
class Article(models.Model, AdminMixin):
    '''文章模型'''
    IMG_LINK = '/static/app_blog/images/occupying.png'
    STATUS_CHOICES = (('d', '草稿'), ('p', '发布'),)

    tags = TaggableManager(through=CnTaggedItem, blank=True)  # 添加标签管理器
    title = models.CharField('标题', max_length=250)
    # slug 字段用于 URL 中，仅包含字母数字下划线以及连字符。根据 slug 字段，可对博客构建具有良好外观和 SEO 友好的 URL。
    # 使用 unique_for_date 参数可采用发布日期与 slug 对帖子构建URL
    slug = models.SlugField('slug', unique_for_date='pub_time', blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_articles', verbose_name='作者')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='blog_articles', verbose_name='分类', blank=False, null=False)
    users_like = models.ManyToManyField(User, related_name='blog_liked', blank=True)

    # body = RichTextUploadingField('正文')
    body = MDTextField('正文')
    img_link = models.CharField('图片地址', default=IMG_LINK, max_length=255)
    summary = models.TextField('文章摘要', max_length=300)
    pub_time = models.DateTimeField('发布时间', default=timezone.now, null=True, blank=True)
    created = models.DateTimeField('创建时间', auto_now_add=True)
    updated = models.DateTimeField('更新时间', auto_now=True)

    article_order = models.IntegerField('排序,数字越大越靠前', blank=True, null=False, default=0)

    views = models.PositiveIntegerField('阅读次数', default=0, blank=True)
    status = models.CharField('文章状态', max_length=10, choices=STATUS_CHOICES, default='d')  # " self.get_status_display  显示完整的信息 "
    is_delete = models.BooleanField('已删除', default=False)
    comment_status = models.BooleanField('是否开启评论', default=True)

    # contenttypes
    comments = GenericRelation(Comments)  # 该字段不会存储于数据库中(用于反向关系查询)

    objects = ModelManager()  # 默认管理器
    published = PublishedManager()  # 自定义的管理器应在默认管理器的后面

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
        # Article.objects.filter(id=article_id).update(pv=F('views')+1)  # 数据库自加, 无竞态问题

    def to_publish(self):
        self.status = 'p'
        self.pub_time = timezone.now()
        self.save(update_fields=['status', 'pub_time'])

    def to_draft(self):
        self.status = 'd'
        self.pub_time = None
        self.save(update_fields=['status', 'pub_time'])

    def body_to_markdown(self):
        content, _ = markdown_render(self.body)
        return content


    # 标准 urls
    def get_absolute_url(self):  # 构建URL
        # /detail/<slug:slug>/
        return reverse('app_blog:article_detail', args=(self.slug,))

    @cache_decorator(60 * 60 * 10)
    def visible_comments_count(self):
        return self.comments.show_count()

    def comment_list(self, is_superuser=False):
        '''获取对应文章的所有评论'''
        if is_superuser:
            return self.comments.all() # 查询所有评论

        cache_key = f'article_comments_{self.id}'
        value = cache.get(cache_key)
        if value:
            logger.info(f'获取评论缓存:{cache_key}')
            return value
        else:
            comments = self.comments.filter(is_hide=False)  # 查询所有评论
            cache.set(cache_key, comments, 60 * 100)
            logger.info(f'设置评论缓存:{cache_key}')
            return comments

    @cache_decorator(60 * 60 * 10)
    def get_category_tree(self):
        tree = self.category.get_all_parents()
        names = list(map(lambda c: (c.name, c.get_absolute_url()), tree))
        return names

    @cache_decorator(expiration=60 * 100)
    def next_article(self):
        # 下一篇
        return Article.published.filter(id__gt=self.id).order_by('id').first()

    @cache_decorator(expiration=60 * 100)
    def prev_article(self):
        # 前一篇
        return Article.published.filter(id__lt=self.id).first()

    # 重写save方法
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid4().hex[:10]

        # 模型的验证器不会在调用save()方法的时候自动执行
        # 表单的验证器会在调用save()方法的时候自动执行
        # Django的模型相关源码中，没有is_valid()方法，也不会自动调用full_clean() 方法，所以Django不会自动进行模型验证。
        # 但是它依然提供了四个重要的验证方法，也就是full_clean() 、clean_fields() 、clean() 和 validate_unique()
        # Django的表单系统forms的相关源码中，表单在save之前会自动执行一个is_valid()方法，这个方法里会调用验证器

        # 如果你手动调用了 full_clean() 方法，那么会依次自动调用下面的三个方法
        # clean_fields()：验证各个字段的合法性
        # clean()：验证模型级别的合法性
        # validate_unique()：验证字段的独一无二性
        try:
            self.full_clean()  
            super().save(*args, **kwargs)
        except ValidationError as e:
            from django.core.exceptions import NON_FIELD_ERRORS
            print('验证没通过： %s' % e.message_dict[NON_FIELD_ERRORS])

    # save 前的验证
    # 草稿文章(d)不应该有发布日期( pub_time )
    # 当文章状态为发布(p), 而发布日期为空时，发布日期应该为当前时间
    def clean(self):
        # 不允许草稿条目具有 pub_time
        if self.status == 'd' and self.pub_time is not None:
            self.pub_time = None
            # raise ValidationError({'pub_time': _('草稿文章尚未发布，不应该有发布日期！')})
            # raise ValidationError('草稿没有发布日期. 发布日期已清空。')
        if self.status == 'p' and self.pub_time is None:
            self.pub_time = timezone.now()

