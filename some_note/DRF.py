
from django.db.models.fields import Field


'''
Seializer之间的继承关系:

django.db.models.fields.Field
            ↑
            |
            |
rest_framework.serializers.BaseSerializer   ----→    定义 create, update 抽象方法
            ↑
            |
            |
rest_framework.serializers.Serializer
            ↑
            |
            |
rest_framework.serializers.ModelSerializer  ----→    重写 create, update
'''








# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
# serializers.py
from apps.app_blog.models import Category
from rest_framework import serializers
from .models import Article
from django.contrib.auth import get_user_model

User = get_user_model()

# REST framework 提供了 Serializer 类和 ModelSerializer 类两种方式来自定义序列化器


'''Serializer'''
class ArticleSerializer(serializers.Serializer):
    '''
    read_only=True: 客户端是不需要也不能够通过POST或PUT请求提交相关数据进行反序列化, 前端只有读的权利.
    write_only=True 这个值让前端只会提交，不会再返回给前端，前端只有写的权利

    '''
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(required=True, allow_blank=True, max_length=90)
    body = serializers.CharField(required=False, allow_blank=True)
    author = serializers.ReadOnlyField(source="author.id")
    status = serializers.ChoiceField(choices=Article.STATUS_CHOICES, default='d')
    created = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        """
        创建新的 article 实例.
        """
        return Article.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        使用验证的数据更新并返回一个已存在的 article 实例.
        """

        # validated_data 已经验证转换过的数据
        # init_data 原始的没有经过验证的数据
        instance.title = validated_data.get('title', instance.title)
        instance.body = validated_data.get('body', instance.body)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance


'''ModelSerializer'''
class ArticleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Article
        fields = '__all__'  # 所有字段 | 或指定的字段 fields = [title, body, ...] 返回给前端的json中包含的字段
        read_only_fields = ('id', 'author', 'create_date')


# 如果你希望author不可见并让DRF根据request.user自动补全这个字段
class ArticleSerializer(serializers.ModelSerializer):
    # HiddenField 隐藏字段
    # serializers.CurrentUserDefault() 提取 request 中的 user
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())  

    class Meta:
        model = Article
        fields = '__all__'  # 所有字段 | 或指定的字段 fields = [title, body, ...] 返回给前端的json中包含的字段
        read_only_fields = ('id', 'create_date')


    # goods = serializers.SerializerMethodField()
    # # 自定义字段
    # # 该方法的命名为 get_ 加上要序列化的字段
    # def get_ad_goods(self, obj):
    #     print('get_ad_goods', obj.id)
    #     goods_json = {}
    #     # 这里传过来的只有'蔬菜水果','酒水饮料','粮油副食','生鲜食品'
    #     # 而他们的序号已经在IndexAd表中添加过了，所有会找到队友的商品纪录
    #     ad_goods = Category.objects.filter(category_id=obj.id, )
    #     if ad_goods:
    #         good_ins = ad_goods[0].goods
    #         # 在serializer的方法中使用Serializer的时候，他会检察上下文中有没有包含request,
    #         # 如果有，那么在返回的图片url中会自动加上域名 http://....
    #         # 如果没有，那么返回的url只会加上路径 /media/goods/images/......
    #         goods_json = GoodsSerializer(good_ins, many=False, context={'request': self.context['request']}).data
    #     return goods_json


# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
# views.py

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Article
from .serializers import ArticleSerializer


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
def article_list(request):
    """
    列出所有的 articles, 或创建 article.
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
        # NOTE: 使用 GenericAPIView 时会自动处理context, 而 APIView 不会, 
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
    使用基础的APIView类
    使用Mixins类和GenericAPI类混配
    使用通用视图generics.*类, 比如generics.ListCreateAPIView
    使用视图集ViewSet和ModelViewSet
'''

# 基础 APIView 类
from rest_framework.views import APIView
from django.http import Http404
from .models import Article
from .serializers import ArticleSerializer

class ArticleList(APIView):
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


class ArticleDetail(APIView):
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








# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
# urls.py 

'''
给URLs添加可选的格式后缀:
    为了充分利用我们的响应不再与单一内容类型连接,
    我们可以为API路径添加对格式后缀(.json或.api)的支持.
    使用格式后缀给我们明确指定了给定格式的 URL,
    能让我们的API将能够处理诸如 http://example.com/api/items/4.json之类的URL
'''
# 首先要给视图函数添加一个 format=None 关键字参数
def article_list(request, format=None):
    ...
def article_detail(request, pk, format=None):
    ...


from django.urls import re_path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    re_path(r'^articles/$', views.article_list),
    re_path(r'^articles/(?P<pk>[0-9]+)$', views.article_detail),]

urlpatterns = format_suffix_patterns(urlpatterns)

























