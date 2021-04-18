# pip install pyjwt

'''
检查用户的认证模式，同时认证完成后验证用户是否有权限操作
兼容session认证的方式，同时支持JWT，并且两种验证共用同一套权限系统
'''

from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied

import jwt

UserModel = get_user_model()

'''检查用户的认证模式，同时认证完成后验证用户是否有权限操作'''
def auth_permission_required(perm):
    '''检查用户的认证模式，同时认证完成后验证用户是否有权限操作'''
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            # 格式化权限
            perms = (perm,) if isinstance(perm, str) else perm

            if request.user.is_authenticated:  # session 验证
                # 正常登录用户判断是否有权限
                if not request.user.has_perms(perms):  # 检查用户权限
                    raise PermissionDenied
            else:
                try:
                    auth = request.META.get('HTTP_AUTHORIZATION').split()  # 获取 token (jwt)  {'Authorization': 'Token '+token})
                except AttributeError:
                    return JsonResponse({"code": 401, "message": "No authenticate header"})

                # 用户通过API获取数据验证流程
                if auth[0].lower() == 'token':
                    try:
                        dict = jwt.decode(auth[1], settings.SECRET_KEY, algorithms=['HS256'])
                        username = dict.get('data').get('username')
                    except jwt.ExpiredSignatureError:  # 过期
                        return JsonResponse({"status_code": 401, "message": "Token expired"})
                    except jwt.InvalidTokenError:  # 非法
                        return JsonResponse({"status_code": 401, "message": "Invalid token"})
                    except Exception as e:  # 载荷信息不存在
                        return JsonResponse({"status_code": 401, "message": "Can not get user object"})

                    try:
                        user = UserModel.objects.get(username=username)  # 检查用户是否存在
                    except UserModel.DoesNotExist:
                        return JsonResponse({"status_code": 401, "message": "User Does not exist"})

                    if not user.is_active:  # 检查用户是否有效
                        return JsonResponse({"status_code": 401, "message": "User inactive or deleted"})

                    # Token登录的用户判断是否有权限
                    if not user.has_perms(perms):  # 检查用户权限
                        return JsonResponse({"status_code": 403, "message": "PermissionDenied"})
                else:  
                    return JsonResponse({"status_code": 401, "message": "Not support auth type"})  # 没有找到 session 和 token

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


# usage
@auth_permission_required('app_name.select_user')
def user(request):
    if request.method == 'GET':
        _jsondata = {
            "user": "ops-coffee",
            "site": "https://ops-coffee.cn"
        }
        return JsonResponse({"state": 1, "message": _jsondata})
    else:
        return JsonResponse({"state": 0, "message": "Request method 'POST' not supported"})


# 给 User model 添加一个token的静态方法来生成用户Token
import datetime
from django.db import models
from django.conf import settings
class User(models.Model):
    ...

    @property
    def token(self):
        return self._generate_jwt_token()
 
    def _generate_jwt_token(self):
        '''生成token'''
        headers = {"type":"jwt", "alg":"HS256"}
        payload = {
            'exp': datetime.datetime.now() +  datetime.timedelta(days=1),  # 过期时间
            'iat': datetime.datetime.now(),  # 签发时间
            'data': {'username': self.username}  # 私有的声明
        }
        # jwt.encode(payload, 加盐, 加密方式, headers)
        token = jwt.encode(payload, settings.SECRET_KEY, 'HS256', headers)
        return token.decode('utf-8')

    @staticmethod
    def parse_payload(token, salt=None):
        """解密token"""
        if not salt: salt = settings.SECRET_KEY
        result = {"status":False,"data":None,"error":None}
        try:
            verified_payload = jwt.decode(token, salt, True)
            result["status"] = True
            result['data']=verified_payload
        except jwt.ExpiredSignatureError: result['error'] = 'token已失效'
        except jwt.DecodeError: result['error'] = 'token认证失败'
        except jwt.InvalidTokenError: result['error'] = '非法的token'
        return result
