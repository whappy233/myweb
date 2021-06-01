from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from loguru import logger

from .models import UserProfile




@receiver(user_logged_in)
def post_login(sender, user, request, **kwargs):
    logger.info(f'USER: {user}(id:{user.id}) 登录.')
    print(f'USER: {user}(id:{user.id}) 登录.')


@receiver(user_logged_out)
def post_logout(sender, user, request, **kwargs):
    logger.info(f'USER: {user}(id:{user.id}) 登出.')
    print(f'USER: {user}(id:{user.id}) 登出.')

USER_MODEL = get_user_model()

# 创建 User 对象实例时也创建 Profile 对象实例
@receiver(post_save, sender=USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    # sender:   发送者模型 <class 'django.contrib.auth.models.User'>
    # instance: 新创建的模型实例
    # created:  True or False
    # kwargs:   {
    #           'signal': <django.db.models.signals.ModelSignal object at 0x10814f550>, 
    #           'update_fields': None, 
    #           'raw': False, 
    #           'using': 'default'
    #           }
    if created:
       UserProfile.objects.create(user=instance)

@receiver(post_save, sender=USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)


# 当删除 UserProfile 时, 同时删除关联的 User 对象.
@receiver(post_delete, sender=UserProfile)
def post_delete_user(sender, instance, *args, **kwargs):
    # if instance.user: # 以防万一未指定用户
    #     instance.user.delete()
    ...