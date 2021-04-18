from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q


# 自定义验证后端
class CustomBackend(ModelBackend):
    """实现用户名邮箱手机号登录"""
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 不希望用户存在两个，get只能有一个。两个是get失败的一种原因 Q为使用并集查询
            user = get_user_model().objects.get(Q(username=username) | Q(email=username) | Q(profile__telephone=username))
            # UserProfile 继承的 AbstractUser 中有 def check_password(self, raw_password):
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class CustomBackend1(ModelBackend):
    """允许使用用户名或邮箱登录"""
    def authenticate(self, request, username=None, password=None, **kwargs):
        if '@' in username:
            kwargs = {'email': username}
        else:
            kwargs = {'username': username}
        try:
            user = get_user_model().objects.get(**kwargs)
            if user.check_password(password):
                return user
        except get_user_model().DoesNotExist:
            return None

    def get_user(self, username):
        try:
            return get_user_model().objects.get(pk=username)
        except get_user_model().DoesNotExist:
            return None