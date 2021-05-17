from django.db.models.signals import post_save
from .models import Comments
from django.dispatch import receiver




# 新建评论通知
@receiver(post_save, sender=Comments) # 激活方式一
def notify_handler(sender, instance, created, **kwargs):

    c_type = instance.content_type
    c_id = instance.object_id
    c_obj = instance.content_object

    comment_author = instance.author
    parent_comment = instance.parent_comment
    # 判断是否是第一次生成评论，后续修改评论不会再次激活信号
    if created:
        if parent_comment:  # 是否有父级
            print('回复的作者', parent_comment.author)
        print('评论的对象', f'({c_type}: {c_id}) {c_obj.title}')
        print('当前评论作者', comment_author)

# post_save.connect(notify_handler, sender=Comments)  # 激活方式二
