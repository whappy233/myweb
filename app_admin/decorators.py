
from django.core.exceptions import PermissionDenied # 权限拒绝异常
from functools import wraps
from django.shortcuts import redirect

# 超级管理员用户需求
def superuser_only(redirect_url='', *args, **kwargs):
    """限制视图只有超级管理员能够访问"""
    def wrapper(function):
        @wraps(function)
        def _inner(request, *args, **kwargs):
            if request.user.is_authenticated:
                if not request.user.is_superuser:
                    if redirect_url:
                        return redirect(redirect_url, *args, **kwargs)
                    raise PermissionDenied
            else:
                if redirect_url:
                    return redirect(redirect_url, *args, **kwargs)
                raise PermissionDenied
            return function(request, *args, **kwargs)
        return _inner
    return wrapper