from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

@receiver(user_logged_in)
def post_login(sender, user, request, **kwargs):
    print('有一个人登录了')
    print(sender)
    print(user)
    print(request)
    print(kwargs)