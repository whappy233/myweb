from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from loguru import logger

@receiver(user_logged_in)
def post_login(sender, user, request, **kwargs):
    logger.info(f'USER: {user}(id:{user.id}) 登录.')
    print(f'USER: {user}(id:{user.id}) 登录.')


@receiver(user_logged_out)
def post_logout(sender, user, request, **kwargs):
    logger.info(f'USER: {user}(id:{user.id}) 登出.')
    print(f'USER: {user}(id:{user.id}) 登出.')



