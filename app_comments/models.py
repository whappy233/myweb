from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType



# 评论模型
class Comments(models.Model):
    '''评论模型'''
    body = models.TextField('正文')
    author = models.ForeignKey(User, verbose_name='作者', on_delete=models.CASCADE)
    parent_comment = models.ForeignKey('self', verbose_name="上级评论", blank=True, null=True, on_delete=models.CASCADE)
    is_active = models.BooleanField('是否显示', default=True)
    created = models.DateTimeField('创建时间', auto_now_add=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name='关联对象类型')   # step1 内容类型，代表了模型的名字(比如Article, Picture)
    object_id = models.PositiveIntegerField('关联对象ID')  # step2 传入对象的id
    content_object = GenericForeignKey('content_type', 'object_id') # step3 传入的实例化对象，其包含两个属性content_type和object_id

    class Meta:
        ordering = ('created',)
        verbose_name = '评论'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.body} (Link_model: {self.content_type}, id: {self.object_id})'


