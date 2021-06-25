'''
@api_view:
    强调这是API视图, 并限定了可以接受的请求方法.
    拓展了 django 原来的 request 对象.
    新的 request 对象不仅仅支持 request.POST 提交的数据, 还支持其它请求方式如 PUT 或 PATCH 等方式提交的数据,
    所有的数据都在 request.data 字典里.

    request.POST  # 只处理表单数据, 只适用于'POST'方法.
    request.data  # 处理任意数据, 适用于'POST'，'PUT'和'PATCH'方法.

Response: 响应对象
    统一使用 Response 方法返回响应, 该方法支持内容协商, 可根据客户端请求的内容类型返回不同的响应数据.

Status: 状态码
    status.HTTP_400_BAD_REQUEST
    status.HTTP_201_CREATED
    ....


NOTE: 使用 GenericAPIView 时会自动处理 context, 而 APIView 不会, 
在所有 APIView 视图中序列化应该传递额外的 context 参数: context={'request': request}

'''


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, generics, mixins, permissions

from django.http import Http404

from apps.app_blog.models import Article
from .serializers import ArticleSerializer
from .permissions import IsOwnerOrReadOnly



'''
函数视图
'''
@api_view(['GET', 'POST'])
def article_list(request):
    """列出所有的 articles, 或创建 article."""

    if request.method == 'GET':
        articles = Article.objects.all()
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)
        # return JSONResponse(serializer.data)

    elif request.method == 'POST':
        serializer = ArticleSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # NOTE: 将 request.user 与作者关联
            # 由于序列化器中 author 是 read-only 字段, 用户是无法通过POST提交来修改的,
            # 在创建 Article 实例时需手动将 author 和 request.user 绑定.
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            # return JSONResponse(serializer.data, status=201)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # return JSONResponse(serializer.errors, status=400)

@api_view(['GET', 'PUT', 'DELETE'])
def article_detail(request, pk):
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
        serializer = ArticleSerializer(article, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



'''
类视图 APIView, GenericAPIView 和视图集 ViewSet.
DRF推荐使用基于类的视图(CBV)来开发API, 并提供了4种开发CBV开发模式。
    APIView 类: 可读性最高、代码最多、灵活性最高. 当你需要对的API行为进行个性化定制时，建议使用这种方式.
    Mixins 类和 GenericAPI类混配: 可读性好、代码适中、灵活性较高。当你需要对一个模型进行标准的增删查改全部或部分操作时建议使用这种方式.
    通用视图 generics.*类, 比如 generics.ListCreateAPIView: 同上.
    视图集 ViewSet 和 ModelViewSet: 可读性较低、代码最少、灵活性最低。当你需要对一个模型进行标准的增删查改的全部操作且不需定制API行为时建议使用这种方式.
'''
class ArticleListAPIView(APIView):
    """列出所有的 articles, 或创建 article."""

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


class ArticleDetailAPIView(APIView):
    """检索、更新或删除文章实例."""

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


# --------------------------------------------------------------------------
# 使用混合（mixins）
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
class ArticleListMixinView(mixins.ListModelMixin, 
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

class ArticleDetailMixinView(mixins.RetrieveModelMixin,
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


# --------------------------------------------------------------------------
# 使用通用视图Generics.*类 
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
class ArticleListGenericsView(generics.ListCreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    # 权限
    # IsAuthenticatedOrReadOnly 确保经过身份验证的请求获得读写访问权限, 未经身份验证的请求将获得只读读的权限
    permission_classes = (permissions.IsAdminUser,)  

    # 将request.user与author绑定
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class ArticleDetailGenericsView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    # 权限
    # IsAuthenticatedOrReadOnly 确保经过身份验证的请求获得读写访问权限, 未经身份验证的请求将获得只读读的权限
    # IsOwnerOrReadOnly 只允许文章的创建者才能编辑
    permission_classes = (permissions.IsAdminUser, IsOwnerOrReadOnly)


