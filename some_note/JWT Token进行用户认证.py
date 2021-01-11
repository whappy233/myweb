
'''
=================================================================================
手动生成Token
'''
from django.core import signing
import hashlib

HEADER={
    'type':'JWT',
    'alg':'HS256'
}

def Encrypt(value):
    '''加密'''
    data=signing.dumps(value)
    data=signing.b64_encode(data.encode()).decode()
    return data

def Decrypt(value):
    '''解密'''
    data=signing.b64_decode(value.encode()).decode()
    data=signing.loads(data)
    return data

def Token(headers, payloads):
    header=Encrypt(headers)
    payload=Encrypt(payloads)
    md5=hashlib.md5()
    md5.update(f"{header}.{payload}".encode())
    signature=md5.hexdigest()
    token=f"{header}.{payload}.{signature}"
    return token

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.http import JsonResponse, HttpResponse
import time
def login(request):
    username = request.POST.get('username').strip()
    password = request.POST.get('password').strip()
    user = authenticate(username=username, password=password)
    if user:
        headers=HEADER
        data={'phone': user.phone, 'mail': user.mail}
        payloads={'iss': user.name, 'iat':time.time()}
        token=Token(headers, payloads)
        info={'token':token}
        info['code']=200
        info['data']=data
        return JsonResponse(info)
    else:
        return  HttpResponse('400')

# 在实际工作中我们最好借助第三方库来实现jwt token认证, 比如 djangorestframework-jwt, 而不是自己生成jwt token.
# 如果要实现跨域的api请求, 还要借助于django-cors-headers这个第三方包.
# pip install djangorestframework-jwt
# pip install django-cors-header

'''
=================================================================================
使用 djangorestframework-jwt
'''
# 1. 安装:
# pip install djangorestframework-jwt


# 2. 在你的settings.py
# 添加 JSONWebTokenAuthentication 到 Django REST 框架 DEFAULT_AUTHENTICATION_CLASSES
# SessionAuthentication 和 BasicAuthentication 在使用 restframework 的调试界面需要用到的模块
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
}


# 3. urls.py
from django.urls import path, re_path, include
from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token
urlpatterns = [
    path('login/', obtain_jwt_token),          # 用于获取token
    path('token-verify/', verify_jwt_token),   # 验证令牌是否合法
    path('api-auth/', include('rest_framework.urls')), # 为restframework调试页面也开启验证
]


# 4. views.py
# 用于认证和授权的装饰器函数
from functools import wraps
from jwt.exceptions import ExpiredSignatureError
def group_required(*required_group_names, method_map=None):
    """
    校验用户是否登录并且属于要求的用户组中的一个
    :param required_group_names: 视图集要求的各个用户组名称
    :param method_map: 对于指定方法要求的用户组名称{方法名:(用户组)}
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            token = request.META.get('HTTP_AUTHORIZATION', None)
            if not token:
                return JsonResponse({'code': 0, 'msg': '失败，尚未登录', 'data': {}}, status=status.HTTP_401_UNAUTHORIZED)
            try:
                jwt_info = jwt.decode(token.split()[-1], SECRET_KEY)
            except ExpiredSignatureError:
                return JsonResponse({'code': 0, 'msg': '失败，登录已超时', 'data': {}}, status=status.HTTP_401_UNAUTHORIZED)
            if jwt_info['is_superuser']:
                return view_func(request, *args, **kwargs)
            # 对于指定方法的校验，用户不属于要求组中的任何一个则认证失败
            if method_map and request.method in method_map:
                if set(method_map[request.method]).isdisjoint(set(jwt_info['groups'])):
                    return JsonResponse({'code': 0, 'msg': '失败，无访问权限', 'data': {}}, status=status.HTTP_403_FORBIDDEN)
                return view_func(request, *args, **kwargs)
            # 通用方法校验，用户不属于要求组中的任何一个则认证失败
            if set(required_group_names).isdisjoint(set(jwt_info['groups'])):
                return JsonResponse({'code': 0, 'msg': '失败，无访问权限', 'data': {}}, status=status.HTTP_403_FORBIDDEN)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

# 使用示例
from django.utils.decorators import method_decorator
@method_decorator(group_required('订单管理员', method_map={'GET': ('订单管理员', '仓库管理员')}), name='dispatch')
class OrderViewSet(CustomModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filterset_class = OrderFilter

# 使用说明:
# 登录获得 token:每次登录成功就得到 jwt_response_payload_handler 返回的 token, 
# 然后访问 api 的时候在请求头的 Authorization 字段带上 token，格式是JWT <token>。

# 通过 token 认证授权:给 ModelViewSet 类的 dispatch 方法加装饰器要使用 method_decorator,
# 装饰器函数的 *required_group_names 参数是视图集类里面所有方法都要求的用户组,
# 上例中订单视图集的各个方法都要求只有订单管理员用户组的成员才可以访问，method_map 是针对个别方法的特殊授权要求，
# 先匹配method_map里的http方法，如果匹配上了就按照这个字典里设置的授权组进行验证，
# 没匹配上的再去验证*required_group_names。上例就是仓库管理员也可以查看订单