

'''header'''
# jwt的头部承载两部分：声明类型，声明加密算法
headers={"type":"JWT","alg":"HS256"}
# 然后将头部进行base64加密。(该加密是可以对称解密的)，构成了第一部分
# eyJ0eXBlIjoiSldUIiwiYWxnIjoiSFMyNTYifQ==


'''playload'''
# 包含三部分：

# 标准中注册声明(建议不强制使用)：
# iss:jwt签发者。
# sub:jwt所面向的用户
# aud:接收jwt的一方
# exp:jwt过期时间，这个过期时间必须大于签发时间
# nbf:定义在什么时间之前，该jwt都是不可用的
# lat:jwt的签发时间
# jti:jwt的唯一身份表示，主要用来作为一次性token,从而回避重放攻击。

# 公共的声明：
# 可以添加任何信息，一般添加用户相关信息。但不建议添加敏感信息，因为该部分在客户端可解密

# 私有的声明：
# 私有声明是提供者和消费者所共同定义的声明，一般不建议存放敏感信息，因为base64是对称解密的，意味着该部分信息可以归类为明文信息。
{
	"username": "xjk",
}


'''signature'''
# 由三部分组成：
# header(base64后的)
# payload(base64后的)
# secret
# 这个部分需要base64加密后的header和base64加密后的pyload使用，连接组成的字符串，然后通过header中声明加密方式，进行加盐secret组合加密，这样构成第三部分



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
rest_framework_jwt是封装jwt符合restful规范接口
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
    path('login/', obtain_jwt_token),          # 登录成功生成 token
    path('token-verify/', verify_jwt_token),   # 验证令牌是否合法
    path('api-auth/', include('rest_framework.urls')), # 为 restframework 调试页面也开启验证
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


'''
=================================================================================
pip install pyjwt
使用 pyjwt
'''
import jwt
import datetime
from jwt import exceptions
# 加的盐
JWT_SALT = "ds()udsjo@jlsdosjf)wjd_#(#)$"

def create_token(payload,timeout=20):
    headers = {"type":"jwt", "alg":"HS256"}
    payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(minutes=20)  # 设置过期时间
    result = jwt.encode(payload=payload, key=JWT_SALT, algorithm="HS256", headers=headers).decode("utf-8")
    return result

def parse_payload(token):
    """解密"""
    result = {"status":False,"data":None,"error":None}
    try:
        verified_payload = jwt.decode(token, JWT_SALT, True)
        result["status"] = True
        result['data']=verified_payload
    except jwt.ExpiredSignatureError: result['error'] = 'token已失效'
    except jwt.DecodeError: result['error'] = 'token认证失败'
    except jwt.InvalidTokenError: result['error'] = '非法的token'
    return result

# 中间件进行jwt校验 middlewares/jwt.py
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
class JwtAuthorizationMiddleware(MiddlewareMixin):
    """
    用户需要通过请求头的方式来进行传输token，例如：
    Authorization:jwt eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1NzM1NTU1NzksInVzZXJuYW1lIjoid3VwZWlxaSIsInVzZXJfaWQiOjF9.xj-7qSts6Yg5Ui55-aUOHJS4KSaeLq5weXMui2IIEJU
    """

    def process_request(self, request):
        '''在到达views之前'''

        # 如果是登录页面，则通过
        if request.path_info == '/login/': return

        # 非登录页面需要校验token
        authorization = request.META.get('HTTP_AUTHORIZATION', '')  # jwt eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl.....
        auth = authorization.split()
        # 验证头信息的token信息是否合法
        if not auth: return JsonResponse({'error': '未获取到Authorization请求头', 'status': False})
        if auth[0].lower() != 'jwt': return JsonResponse({'error': 'Authorization请求头中认证方式错误', 'status': False})
        if len(auth) == 1: return JsonResponse({'error': "非法Authorization请求头", 'status': False})
        elif len(auth) > 2: return JsonResponse({'error': "非法Authorization请求头", 'status': False})

        token = auth[1]  # eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.gdfgd.....
        result = parse_payload(token)  # 解密
        if not result['status']: return JsonResponse(result)
        # 将解密后数据赋值给user_info
        request.user_info = result['data']



