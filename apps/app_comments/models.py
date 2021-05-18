from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now
from django.db.models import Q

# 游民信息表
class Wanderer(models.Model):
    username = models.CharField('昵称', max_length=20)
    email = models.EmailField('邮箱', max_length=30, unique=True)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '游民信息'
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        return f'{self.id}: {self.username}-{self.email}'


# 评论模型
class Comments(models.Model):
    '''评论模型'''
    body = models.TextField('评论内容', max_length=500)

    # user_obj.comments.all() 某 user 下的所有评论
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='comments',
                               blank=True, null=True,
                               verbose_name='作者')

    # wanderer_obj.comments.all() 某 wanderer 下的所有评论
    wanderer = models.ForeignKey(Wanderer, on_delete=models.CASCADE,
                                 related_name='comments',
                                 blank=True, null=True,
                                 verbose_name='散人')

    # comment_obj.child_comments.all() 某评论下的所有子评论
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE,
                                       related_name='child_comments',
                                       blank=True, null=True,
                                       verbose_name="上级评论")

    is_overhead = models.BooleanField('是否顶置', default=False)
    is_visible = models.BooleanField('是否可见', default=True)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_mod_time = models.DateTimeField('修改时间', default=now)

    # 使用admin呈现此字段时，设置对此字段(limit_choices_to)的可用选项的限制(默认情况下, 查询集中的所有对象都可供选择).
    # 可以使用字典、Q对象或可调用返回字典或Q对象.

    # step1 内容类型，代表了模型的名字(比如Article, Picture)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                                     limit_choices_to={
                                         "model__in": ("article", 'photo')
                                     },
                                     verbose_name='关联对象类型')
    # step2 传入对象的id
    object_id = models.PositiveIntegerField('关联对象ID')
    # step3 传入的实例化对象，其包含两个属性content_type和object_id
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ('last_mod_time',)
        verbose_name = '评论'
        verbose_name_plural = verbose_name

        # 添加约束
        # 条件约束确保一个模型实例只有满足一定的规则条件后才被创建，不满足条件的数据不会存入到数据库。
        constraints = [ 
            # 只有 user 或 wanderer 存在才允许存到数据库
            models.CheckConstraint(check=Q(author__isnull=False)|Q(wanderer__isnull=False), 
            name='User 或 Wanderer 至少存在其中一个!'),
        ]

    def save(self, *args, **kwargs):
        if self.is_overhead == True and self.parent_comment:
            raise ValueError('不允许顶置非顶级评论')

        # 当 user 和 wanderer 同时存在时, 清除 wanderer 
        if self.author and self.wanderer:
            self.wanderer = None
        super().save(*args, **kwargs)


    def __str__(self):
        return f'{self.id}:{self.body} (关联对象:{self.content_type} id:{self.object_id})'
