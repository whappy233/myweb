
from app_common.email import send_email_by_template
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Comments

# 新建评论通知
@receiver(post_save, sender=Comments)  # 激活方式一
def notify_handler(sender, instance, created, **kwargs):

    c_type = instance.content_type  # 评论关联的模型
    c_id = instance.object_id       # 评论关联模型的 id
    c_obj = instance.content_object # 评论关联模型的实例

    parent_comment = instance.parent_comment  # 评论的父评论

    # 判断是否是第一次生成评论，后续修改评论不会再次激活信号
    if created:
        if parent_comment:  # 是否有父级
            print('回复的作者', parent_comment.author)
            print('回复的评论', parent_comment.body)
        print('评论的对象', f'({c_type}: {c_id}) {c_obj.title} {c_obj.get_absolute_url()}')
        print('当前评论作者', instance.author)
        print('当前评论内容', instance.body)

        try:
            # 设置模版对应的参数
            email_data = {
                'comment_name': instance.author,
                'comment_content': instance.body,
                'comment_url': c_obj.get_absolute_url()}
            subject = ''  # 邮件主题
            template = ''  # 使用的模版
            to_list = []  # 收件人

            if not parent_comment:
                subject = u'[浩瀚星海]博文评论'
                template = 'app_comments/comments_email.html'
                # 发送给自己（可以写其他邮箱）
                to_list.append('whh369@foxmail.com')
            else:
                subject = u'[浩瀚星海]评论回复'
                template = 'app_comments/comments_email_reply.html'
                # 获取评论对象，找到回复对应的评论
                # comment_model = django_comments.get_model()
                # cams = comment_model.objects.filter(id = comment.reply_to)
                # if cams:
                # to_list.append(cams[0].user_email)
                # else:
                # 没有找到评论，就发给自己（可以修改其他邮箱）
                to_list.append('whh369@foxmail.com')

            # 根据模版发送邮件
            send_email_by_template(subject, template, email_data, to_list)

        except Exception as e:
            print(20*'-')
            print(e)


# post_save.connect(notify_handler, sender=Comments)  # 激活方式二


