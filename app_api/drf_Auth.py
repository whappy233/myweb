

'''
在DRF中设置认证方案
'''

# 设置默认的全局认证方案
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )}


# 在基于类的视图(CBV)中使用
from rest_framework import views
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework import permissions
from rest_framework.response import Response
class ExampleView(views.APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)  # 认证
    permission_classes = (permissions.IsAuthenticated,)  # 权限


# 在基于函数的视图中使用
from rest_framework.decorators import api_view, authentication_classes, permission_classes
@api_view(['GET'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((permissions.IsAuthenticated,))
def example_view(request, format=None):
    content = {
        'user': request.user,  # `django.contrib.auth.User` 实例。
        'auth': request.auth   # None
    }
    return Response(content)




'''
------------------------------------------------------------------------------------------
NOTE: 自定义认证方案

要实现自定义的认证方案，首先要继承 BaseAuthentication 类并且重写 .authenticate(self, request) 方法。
如果认证成功，该方法应返回 (user, auth) 的二元元组，否则返回 None.

在某些情况下，你可能不想返回None，而是希望从 .authenticate() 方法抛出 AuthenticationFailed 异常。
通常你应该采取的方法是：
    1. 如果不尝试验证，返回 None。还将检查任何其他正在使用的身份验证方案。
    2. 如果尝试验证但失败，则抛出 AuthenticationFailed 异常。
       任何权限检查不再检查任何其他身份验证方案, 立即返回错误响应。
    3. 你也可以重写 .authenticate_header(self, request) 方法。
       如果实现该方法，则应返回一个字符串，该字符串将用作 HTTP 401 Unauthorized 响应中的 WWW-Authenticate 头的值。
       如果 .authenticate_header() 方法未被重写，则认证方案将在未验证的请求被拒绝访问时返回 HTTP 403 Forbidden 响应。

'''
# 示例
from django.contrib.auth.models import User
from rest_framework import authentication
from rest_framework import exceptions

class ExampleAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        # 将自定义请求标头中名称为 'X_USERNAME' 提供的用户名作为用户对任何传入请求进行身份验证,
        # 其它类似自定义认证需求比如支持用户同时按用户名或email进行验证.
        username = request.META.get('X_USERNAME')
        if not username:
            return None

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('用户不存在')

        return (user, None)




'''
------------------------------------------------------------------------------------------
使用 TokenAuthentication
'''

# 首先，你需要将修改settings.py, 加入如下app。
# settings.py
INSTALLED_APPS = (
    ...,
    'rest_framework.authtoken',
    ...
    )
# 其次，你需要为你的用户生成令牌(token)。如果你希望在创建用户时自动生成token，你可以借助Django的信号(signals)实现，如下所示：

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

# 如果你已经创建了一些用户，则可以打开shell为所有现有用户生成令牌，如下所示：
'''    
    from django.contrib.auth.models import User
    from rest_framework.authtoken.models import Token
    for user in User.objects.all():    
        Token.objects.get_or_create(user=user)
'''


# 你还可以在admin.py中给用户创建token，如下所示：
from rest_framework.authtoken.admin import TokenAdmin
TokenAdmin.raw_id_fields = ['user']


'''
从3.6.4起，你还可以使用如下命令为一个指定用户新建或重置token。
./manage.py drf_create_token <username> # 新建
./manage.py drf_create_token -r <username> # 重置
'''

# 接下来，你需要暴露用户获取token的url地址(API端点).
from rest_framework.authtoken import views
from django.urls import re_path, path
urlpatterns = [...]
urlpatterns += [
    re_path(r'^api-token-auth/', views.obtain_auth_token)]
# 这样每当用户使用form表单或JSON将有效的username和password字段POST提交到以上视图时，obtain_auth_token 视图将返回如下JSON响应：
# { 'token' : '9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b' }

# 客户端拿到token后可以将其存储到本地cookie或localstorage里，下次发送请求时把token包含在Authorization HTTP头即可，如下所示：

'''
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
你还可以通过curl工具来进行简单测试。
curl -X GET http://127.0.0.1:8000/api/example/ -H 'Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b'
'''



'''
自定义Token返回信息
默认的obtain_auth_token视图返回的json响应数据是非常简单的，只有token一项。如果你希望返回更多信息，比如用户id或email，就就要通过继承ObtainAuthToken类量身定制这个视图，如下所示:
'''
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })

# 然后修改urls.py:
urlpatterns +=[
    path('api-token-auth/',CustomAuthToken.as_view())]

# 最后一步，DRF 的 TokenAuthentication 类会从请求头中获取 Token，验证其有效性。
# 如果token有效，返回request.user。至此，整个token的签发和验证就完成了.



