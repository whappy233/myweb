from rest_framework import permissions
from rest_framework import generics



"""
NOTE: rest_framework 权限设置:

    1. 在基于类的API视图里通过 permission_classes 属性设置的权限类
    class ArticleList(generics.ListCreateAPIView):
        ...
        permission_classes = (permissions.IsAuthenticatedOrReadOnly, )  
        ...

    2. 在函数视图添加权限
    from rest_framework.decorators import api_view, permission_classes
    from rest_framework import permissions
    from rest_framework.response import Response
    @api_view(['GET'])
    @permission_classes((permissions.IsAuthenticated, ))
    def example_view(request, format=None):
        content = {
            'status': 'request was permitted'
        }
        return Response(content)

    3. 在 settings.py 中使用 DEFAULT_PERMISSION_CLASSES 全局设置默认权限策略
    REST_FRAMEWORK = {
        'DEFAULT_PERMISSION_CLASSES': (
            'rest_framework.permissions.IsAuthenticated',
        )
    }
    如果未指定，则此设置默认为允许无限制访问: 'rest_framework.permissions.AllowAny',
    当你通过类属性或装饰器设置新的权限类时, 视图会覆盖 settings.py 中设置的默认权限
"""


"""
NOTE: 自定义权限
    自定义的权限类需要继承 BasePermission 类并根据需求重写 has_permission(self, request, view)和has_object_permission(self,request, view, obj)

    class CustomerPermission(permissions.BasePermission):
        message = '自定义返回的错误信息.'

        def has_permission(self, request, view):
            ...

        def has_object_permission(self, request, view, obj):
            ...
"""



class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    自定义权限只允许文章的创建者才能编辑它。
    """
    def has_object_permission(self, request, view, obj):
        # 读取权限被允许用于任何请求，
        # 所以我们始终允许 GET，HEAD 或 OPTIONS 请求。
        if request.method in permissions.SAFE_METHODS:
            return True
        # 写入权限只允许给 article 的作者。
        return obj.author == request.user