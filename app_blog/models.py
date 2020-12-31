from django.db import models
from django.db.models import base
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from taggit.managers import TaggableManager  # 第三方标签应用
from ckeditor_uploader.fields import RichTextUploadingField  # 富文本编辑器
import base64


# 自定义的管理器
class PublishedManage(models.Manager):
    def get_queryset(self):
        # 修改管理器的初始 QuerySet
        return super(PublishedManage, self).get_queryset().filter(status='p')

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
class Post(models.Model):
    '''文章模型'''
    tags = TaggableManager()  # 添加标签管理器
    STATUS_CHOICES = (
        ('d', '草稿'),
        ('p', '发布'),
    )
    title = models.CharField('标题', max_length=250)
    # slug 字段用于 URL 中，仅包含字母数字下划线以及连字符。根据 slug 字段，可对博客构建具有良好外观和 SEO 友好的 URL。
    # 使用 unique_for_date 参数可采用发布日期与 slug 对帖子构建URL
    slug = models.SlugField(
        'slug', max_length=250, unique_for_date='publish', blank=True)
    # related_name 指定反向关系名称(从User到Post)
    users_like = models.ManyToManyField(User, related_name='blog_liked', blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts', verbose_name='作者')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='blog_posts', verbose_name='分类', blank=False, null=False)

    body = RichTextUploadingField('正文')
    views = models.PositiveIntegerField('阅读次数', default=0)
    publish = models.DateTimeField('发布时间', default=timezone.now, null=True, blank=True)
    created = models.DateTimeField('创建时间', auto_now_add=True)
    updated = models.DateTimeField('更新时间', auto_now=True)
    status = models.CharField(
        '文章状态', max_length=10, choices=STATUS_CHOICES, default='d')
    is_delete = models.BooleanField(default=False)

    objects = models.Manager()  # 默认管理器
    # objects = aaa()   # 在默认管理器上增加了方法
    published = PublishedManage()  # 自定义的管理器应在默认管理器的后面
    # from django.contrib.auth.models import User
    # from app_blog.models import Post
    # Post.published.filter(title__startswith='w')

    class Meta:
        ordering = ('-publish',)  # 出版日期降序
        verbose_name = '文章'  # 定义一个可读名字
        verbose_name_plural = verbose_name

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
        # <int:year>/<int:month>/<int:day>/<slug:post>/
        # /2020/1/10/markdown/
        a = [self.publish.year, self.publish.month, self.publish.day, self.slug]
        return reverse('app_blog:post_detail', args=a)

    # 重写save方法
    def save(self, *args, **kwargs):
        if not self.slug:
            slug = base64.urlsafe_b64encode(
                self.title.encode()).decode().rstrip('=')
            # print(base64.urlsafe_b64decode(
            #     slug + '=' * (4 - len(slug) % 4)).decode())  # 解码
            self.slug = slug
        super().save(*args, **kwargs)

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
    # related_name 可对对应关系属性进行命名(指定反向关系名称)(从Post到Comment),
    # 如果未定义,Django将使用模型名称_set的形式如:post.comment_set.all()
    # comment.post检索评论对象的帖子
    # post.comments.all()检索某文章的全部评论
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments', verbose_name='关联文章')  # 多对一
    name = models.CharField(max_length=80, verbose_name='名字')
    email = models.EmailField(verbose_name='邮箱')
    body = models.TextField(verbose_name='评论')
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    active = models.BooleanField(default=True, verbose_name='是否有效')  # 隐式删除

    class Meta:
        ordering = ('created',)
        verbose_name = '评论'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '来自 {} 下 {} 的评论'.format(self.post, self.name)
