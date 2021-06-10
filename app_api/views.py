from django.http import Http404
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from rest_framework.views import APIView, get_view_name
from rest_framework import mixins
from rest_framework import generics
from rest_framework import viewsets
from rest_framework import permissions  # 权限类

from .permissions import IsOwnerOrReadOnly  # 自定义权限


from .serializers import ArticleSerializer, UserSerializer, UserProfileSerializer
from app_blog.models import Article
from app_user.models import UserProfile


User = get_user_model()



'''
@api_view:
    强调这是API视图, 并限定了可以接受的请求方法.
    拓展了 django 原来的 request 对象.
    新的 request 对象不仅仅支持 request.POST 提交的数据, 还支持其它请求方式如 PUT 或 PATCH 等方式提交的数据,
    所有的数据都在 request.data 字典里.

    request.POST  # 只处理表单数据, 只适用于'POST'方法.
    request.data  # 处理任意数据, 适用于'POST'，'PUT'和'PATCH'方法.

Response:
    统一使用 Response 方法返回响应, 该方法支持内容协商, 可根据客户端请求的内容类型返回不同的响应数据.

NOTE: 使用 GenericAPIView 时会自动处理 context, 而 APIView 不会, 
在所有 APIView 视图中序列化应该传递额外的 context 参数: context={'request': request}

'''


# 函数视图
@api_view(['GET', 'POST'])
@permission_classes((permissions.IsAuthenticatedOrReadOnly, ))  # 权限
def article_list(request, format=None):
    """
    列出所有的 aricle, 或创建 article.
    """
    if request.method == 'GET':
        articles = Article.objects.all()
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ArticleSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # NOTE: 将 request.user 与作者关联
            # 由于序列化器中 author 是 read-only 字段, 用户是无法通过POST提交来修改的,
            # 在创建 Article 实例时需手动将 author 和 request.user 绑定.
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def article_detail(request, pk, format=None):
    """
    检索、更新或删除文章实例.
    """
    try:
        article = Article.objects.get(pk=pk)
    except Article.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ArticleSerializer(article)
        return Response(serializer.data)

    elif request.method == 'PUT':

        # NOTE: 使用 GenericAPIView 时会自动处理context，而 APIView 不会, 
        # 在所有 APIView 视图中序列化应该传递额外的 context 参数: context={'request': request}

        serializer = ArticleSerializer(article, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



'''
基于类的视图 APIView, GenericAPIView 和视图集 ViewSet.
DRF推荐使用基于类的视图(CBV)来开发API, 并提供了4种开发CBV开发模式。
    APIView 类: 可读性最高、代码最多、灵活性最高. 当你需要对的API行为进行个性化定制时，建议使用这种方式.
    Mixins 类和 GenericAPI类混配: 可读性好、代码适中、灵活性较高。当你需要对一个模型进行标准的增删查改全部或部分操作时建议使用这种方式.
    通用视图 generics.*类, 比如 generics.ListCreateAPIView: 同上.
    视图集 ViewSet 和 ModelViewSet: 可读性较低、代码最少、灵活性最低。当你需要对一个模型进行标准的增删查改的全部操作且不需定制API行为时建议使用这种方式.
'''

# 基础 APIView 类 -------------------------------------------------------------
class ArticleList1(APIView):
    """
    列出所有的 articles, 或创建 article.
    """
    def get(self, request, format=None):
        articles = Article.objects.all()
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ArticleSerializer(data=request.data)
        if serializer.is_valid():
            # 注意：手动将request.user与author绑定
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ArticleDetail1(APIView):
    """
    检索、更新或删除文章实例.
    """
    def get_object(self, pk):
        try:
            return Article.objects.get(pk=pk)
        except Article.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        article = self.get_object(pk)
        serializer = ArticleSerializer(article)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        article = self.get_object(pk)
        serializer = ArticleSerializer(instance=article, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        article = self.get_object(pk)
        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Mixin类和GenericAPI类混配 -----------------------------------------------------
'''
mixins:
    mixins.ListModelMixin       # 多个对象
    mixins.CreateModelMixin     # 创建对象
    mixins.RetrieveModelMixin   # 某个对象
    mixins.UpdateModelMixin     # 更新对象
    mixins.DestroyModelMixin    # 摧毁对象

    钩子函数:
    用于执行创建对象时需要执行的其它方法, 比如发送邮件等功能, 有点类似于 Django 的信号.
        CreateModelMixin.perform_create(serializer)
        UpdateModelMixin.perform_update(serializer)
        DestroyModelMixin.perform_destroy(instance)
'''
class ArticleList2(mixins.ListModelMixin, 
                  mixins.CreateModelMixin, 
                  generics.GenericAPIView):

    # ListModelMixin 和 CreateModelMixin 类则分别引入了 .list() 和 .create() 方法.

    queryset = Article.objects.all()        # 指定需要序列化与反序列化的 queryset
    serializer_class = ArticleSerializer    # 指定序列化器

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    # 将request.user 与 author 绑定。调用 create 方法时执行如下函数.
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class ArticleDetail2(mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    generics.GenericAPIView):

    queryset = Article.objects.all()        # 指定需要序列化与反序列化的 queryset
    serializer_class = ArticleSerializer    # 指定序列化器

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


# 使用通用视图Generics.*类 --------------------------------------------------------
'''
generics:
    generics.ListCreateAPIView 类支持 List、Create 两种视图功能, 分别对应GET和POST请求.
    generics.RetrieveUpdateDestroyAPIView 支持 Retrieve、Update、Destroy 操作, 其对应方法分别是GET、PUT和DELETE.
    generics.ListAPIView, 
    generics.RetrieveAPIView, 
    generics.RetrieveUpdateAPIView
    根据实际需求使用，为你的API写视图时只需要定义queryset和serializer_class即可.
'''
# 文章
class ArticleList(generics.ListCreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    # 权限
    # IsAuthenticatedOrReadOnly 确保经过身份验证的请求获得读写访问权限, 未经身份验证的请求将获得只读读的权限
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)  

    # 将request.user与author绑定
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class ArticleDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    # 权限
    # IsAuthenticatedOrReadOnly 确保经过身份验证的请求获得读写访问权限, 未经身份验证的请求将获得只读读的权限
    # IsOwnerOrReadOnly 只允许文章的创建者才能编辑
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)


# 用户
class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class =UserSerializer


# UserProfile
class UserProfileList(generics.ListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class =UserProfileSerializer






# 使用视图集ViewSet -------------------------------------------------------------
'''
    使用通用视图 generics 类后视图代码已经大大简化,
    但是 ArticleList 和 ArticleDetail 两个类中 queryset 和 serializer_class 属性依然存在代码重复.
    使用视图集可以将两个类视图进一步合并，一次性提供 List、Create、Retrieve、Update、Destroy 这5种常见操作,
    这样 queryset 和 seralizer_class 属性也只需定义一次就好, 这就变成了视图集 (viewset).

    使用视图集后，我们需要使用 DRF 提供的路由 router 来分发 urls, 因为一个视图集现在对应多个urls, 
    而不像之前的一个 url 对应一个视图函数或一个视图类.
    urls.py:
        # 一个视图集对应了 List、Create、Retrieve、Update、Destroy 五种操作.
        from rest_framework.routers import DefaultRouter
        router = DefaultRouter()
        router.register(r'articles', viewset=views.ArticleViewSet)
        urlpatterns += router.urls

        # 视图集指定方法映射(指定需要的操作)
        article_list = views.ArticleViewSet.as_view({
            'get': 'list',
            'post': 'create'
        })

        article_detail = views.ArticleViewSet.as_view({
            'get': 'retrieve',  # 只处理get请求，获取单个记录
        })

        urlpatterns = [
            re_path(r'^articles/$', article_list),
            re_path(r'^articles/(?P<pk>[0-9]+)$', article_detail),
        ]

        urlpatterns = format_suffix_patterns(urlpatterns)
'''
class ArticleViewSet1(viewsets.ModelViewSet):
    # 用一个视图集替代 ArticleList 和A rticleDetail 两个视图
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    # 自行添加，将request.user与author绑定
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class UserProfileViewSet1(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


    # 动态加载序列化器类
    # def get_serializer_class(self):
    #     if self.action == 'create':
    #         return CustomSerializer1
    #     elif self.action == 'list':
    #         return XXXSerializer
    #     return CustomSerializer1


class UserViewSet1(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# class UserViewSet(viewsets.ReadOnlyModelViewSet):
#     """
#     ReadOnlyModelViewSet 仅支持 list 和 retrive 这两个可读的操作.
#     """
#     queryset = UserProfile.objects.all()
#     serializer_class = UserProfileSerializer

