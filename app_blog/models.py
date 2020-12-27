from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from taggit.managers import TaggableManager  # 第三方标签应用


# 自定义的管理器
class PublishedManage(models.Manager):
    def get_queryset(self):
        return super(PublishedManage, self).get_queryset().filter(status='published')  # 修改管理器的初始 QuerySet


# 在默认管理器上增加方法
# class aaa(models.Manager):
#     def get_status(self):
#         try:
#             a = self.get(status='published')
#         except:
#             a = None
#         return  a




# 文章模型
class Post(models.Model):
    tags = TaggableManager()  # 添加标签管理器
    STATUS_CHOICES = (('draft', '草稿'), ('published', '发布'),)
    title = models.CharField(max_length=250, verbose_name='标题')
    # slug 字段用于 URL 中，仅包含字母数字下划线以及连字符。根据 slug 字段，可对博客构建具有良好外观和 SEO 友好的 URL。
    # 使用 unique_for_date 参数可采用发布日期与 slug 对帖子构建URL
    slug = models.SlugField(max_length=250, unique_for_date='publish', blank=True)
    # related_name 指定反向关系名称（从User到Post）
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts', verbose_name='作者')
    body = models.TextField(verbose_name='正文')
    views = models.PositiveIntegerField(verbose_name='阅读次数', default=0)
    publish = models.DateTimeField(default=timezone.now, verbose_name='发表时间')
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
    is_delete = models.BooleanField(default=False)

    objects = models.Manager()  # 默认管理器
    # objects = aaa()   # 在默认管理器上增加了方法
    published = PublishedManage()  # 自定义的管理器应在默认管理器的后面

    # from django.contrib.auth.models import User
    # from app_blog.models import Post
    # Post.publishe.filter(title__startswith='w')

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

    # 模型的标准 urls
    def get_absolute_url(self):  # 构建URL

        # <int:year>/<int:month>/<int:day>/<slug:post>/
        # /2020/1/10/markdown/
        # /2020/1/8/gnzy/
        # /2020/1/4/ghsy/
        # /2020/1/10/markdown/
        return reverse('app_blog:post_detail', args=[self.publish.year, self.publish.month, self.publish.day, self.slug])


    # 重写save方法
    # def save(self, *args, **kwargs):
    #     do_something()
    #     super().save(*args, **kwargs) 
    #     do_something_else()


# 评论模型
class Comment(models.Model):
    # related_name 可对对应关系属性进行命名(指定反向关系名称)(从Post到Comment),如果未定义,Django将使用模型名称_set的形式如:post.comment_set.all()
    # comment.post检索评论对象的帖子
    # post.comments.all()检索某文章的全部评论
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name='关联文章')  # 多对一
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
