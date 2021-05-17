from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now


# 评论模型
class Comments(models.Model):
    '''评论模型'''
    body = models.TextField('正文')
    author = models.ForeignKey(User, verbose_name='作者',
                               on_delete=models.CASCADE)
    parent_comment = models.ForeignKey('self', verbose_name="上级评论",
                                       blank=True, null=True,
                                       on_delete=models.CASCADE)
    is_visible = models.BooleanField('是否可见', default=True)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_mod_time = models.DateTimeField('修改时间', default=now)

    # 使用admin呈现此字段时，设置对此字段(limit_choices_to)的可用选项的限制(默认情况下, 查询集中的所有对象都可供选择).
    # 可以使用字典、Q对象或可调用返回字典或Q对象.

    # step1 内容类型，代表了模型的名字(比如Article, Picture)
    content_type = models.ForeignKey(ContentType,
                                     limit_choices_to={
                                         "model__in": ("article", 'photo')
                                     },
                                     on_delete=models.CASCADE,
                                     verbose_name='关联对象类型')
    # step2 传入对象的id
    object_id = models.PositiveIntegerField('关联对象ID')
    # step3 传入的实例化对象，其包含两个属性content_type和object_id
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ('last_mod_time',)
        verbose_name = '评论'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.id} (关联对象:{self.content_type} id:{self.object_id})'
