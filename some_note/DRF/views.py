'''
@api_view(http_method_names=['GET'], exclude_from_schema=False):
    确保视图函数会收到 Request ( 而不是 Django 一般的 HttpRequest ) 对象, 
    并且返回 Response ( 而不是 Django 的 HttpResponse )对象
    强调这是API视图, 并限定了可以接受的请求方法. exclude_from_schema 参数标记API视图来忽略任何自动生成的视图

Request:
    新的 Request 对象不仅仅支持 request.POST 提交的数据, 还支持其它请求方式如 PUT 或 PATCH 等方式提交的数据,
    所有的数据都在 request.data 字典里.

    request.POST  # 只处理表单数据, 只适用于'POST'方法.

    request.data  # 处理任意数据, 适用于'POST', 'PUT'和'PATCH'方法.
    如果客户端发送格式错误的内容, 则访问request.data可能会引发ParseError, 
    默认情况下 REST framework 的 APIView 类或 @api_view 装饰器将捕获错误并返回400 Bad Request响应.
    如果客户端发送具有无法解析的类型请求, 则会引发 UnsupportedMediaType 异常,
    默认情况下会捕获该异常并返回 415 Unsupported Media Type 响应.

    request.user            通常返回一个 django.contrib.auth.models.User(or AnonymousUser) 实例.
    request.auth            如果请求未认证或者没有其他上下文, 则 request.auth 的默认值为 None.
    request.authenticators  为 Authentication 实例的列表

    request.method          返回请求的方法
    request.content_type    返回表示HTTP请求正文的媒体类型的字符串对象, 如果未提供媒体类型, 则返回空字符串.
    request.stream          返回一个表示请求主体内容的流

Response: 响应对象
    统一使用 Response 方法返回响应, 该方法支持内容协商, 可根据客户端请求的内容类型返回不同的响应数据.
    Response(data, status=None, template_name=None, headers=None, content_type=None)
        data: response的数列化数据.
        status: response的状态码.默认是200.
        template_name: HTMLRenderer 选择要使用的模板名称.
        headers: A dictionary of HTTP headers to use in the response.
        content_type: response的内容类型.通常由渲染器自行设置, 由content negotiation确定, 但是在某些情况下, 你需要明确指定内容类型

Status: 状态码
    status.HTTP_400_BAD_REQUEST
    status.HTTP_201_CREATED
    ....

NOTE: 使用 GenericAPIView 时会自动处理 context, 而 APIView 不会, 
在所有 APIView 视图中序列化应该传递额外的 context 参数: context={'request': request}

'''

from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, action, permission_classes, throttle_classes
from rest_framework.throttling import UserRateThrottle
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, generics, mixins, permissions, viewsets, renderers

from django.http import Http404
from django.contrib.auth.models import User

from apps.app_blog.models import Article
from .serializers import ArticleSerializer, UserSerializer
from .permissions import IsOwnerOrReadOnly


# 使用限制器确保特定用户每天只能调用一次的视图
class OncePerDayUserThrottle(UserRateThrottle):
        rate = '1/day'



'''
------------------------------------------------------------------------------------------------------
函数视图 @api_view
------------------------------------------------------------------------------------------------------
'''
# 可用装饰器 每一个都接受一个参数, 这个参数必须是类的列表或元组
# @renderer_classes((,))
# @parser_classes((,))
# @authentication_classes((,))  # 认证管理
# @throttle_classes((,))        # 节流策略管理
# @permission_classes((,))      # 权限管理

@api_view(['GET', 'POST'])
@throttle_classes((OncePerDayUserThrottle, ))           # API 策略装饰器
@permission_classes((permissions.IsAuthenticated, ))    # 权限装饰器
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
------------------------------------------------------------------------------------------------------
类视图 APIView, GenericAPIView, Mixins, 和视图集 ViewSet.
------------------------------------------------------------------------------------------------------
DRF推荐使用基于类的视图(CBV)来开发API, 并提供了4种开发CBV开发模式.
    APIView 类: 可读性最高、代码最多、灵活性最高. 当你需要对的API行为进行个性化定制时, 建议使用这种方式.
    Mixins 类和 GenericAPI类混配: 可读性好、代码适中、灵活性较高.当你需要对一个模型进行标准的增删查改全部或部分操作时建议使用这种方式.
    通用视图 generics.*类, 比如 generics.ListCreateAPIView: 同上.
    视图集 ViewSet 和 ModelViewSet: 可读性较低、代码最少、灵活性最低.当你需要对一个模型进行标准的增删查改的全部操作且不需定制API行为时建议使用这种方式.

可拔插的属性:
    .renderer_classes
    .parser_classes
    .authentication_classes      # 认证管理
    .throttle_classes            # 节流策略管理
    .permission_classes          # 权限控制
    .content_negotiation_class

用来实例化各种可拔插的API策略的方法:
    .get_renderers(self)
    .get_parsers(self)
    .get_authenticators(self)
    .get_throttles(self)
    .get_permissions(self)
    .get_content_negotiator(self)
    .get_exception_handler(self)

在请求被分发到具体的处理方法之前调用的方法:
    .check_permissions(self, request)
    .check_throttles(self, request)
    .perform_content_negotiation(self, request, force=False)

Dispatch methods 会被视图的 .dispatch() 方法直接调用.
    它们在调用.get, .post(), put(), patch()和delete()之类的请求处理方法之前或者之后执行任何需要执行的操作.

    .initial(self, request, *args, **kwargs)  
        处理方法调用之前进行任何需要的动作. 这个方法用于执行权限认证和限制, 并且执行内容协商.

    .handle_exception(self, exc)
        任何被处理请求的方法抛出的异常都会被传递给这个方法.
        默认的实现会处理 rest_framework.expceptions.APIException的 任何子类异常, 
        以及Django的Http404和PermissionDenied异常, 并且返回一个适当的错误响应
        如果你需要在自己的 API 中自定义返回的错误响应, 你需要重写这个方法.

    .initialize_request(self, request, *args, **kwargs)
        处理方法调用之前. 用于确保传递给请求处理方法的请求对象是 Request 的实例, 而不是通常的 DjangoHttpResquest 的实例

    .finalize_response(self, request, response, *args, **kwargs)
        处理方法调用之后. 用于确保任何从处理请求的方法返回的 Response 对象被渲染到由内容协商决定的正确内容类型
'''

# ----------------------------------------------------------------------------
# APIView
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


# ----------------------------------------------------------------------------
# 混合（mixins）
'''
GenericAPIView 基本设置:
    queryset            用于从视图返回对象的查询结果集.通常, 你必须设置此属性或者重写 get_queryset() 方法.
    serializer_class    用于验证和反序列化输入以及用于序列化输出的Serializer类. 通常, 你必须设置此属性或者重写get_serializer_class() 方法.
    lookup_field        用于执行各个model实例的对象查找的model字段.默认为 'pk'. 请注意, 在使用超链接API时, 如果需要使用自定义的值, 你需要确保在API视图和序列化类都设置查找字段.
    lookup_url_kwarg    应用于对象查找的URL关键字参数.它的 URL conf 应该包括一个与这个值相对应的关键字参数.如果取消设置, 默认情况下使用与 lookup_field相同的值.
    pagination_class    当分页列出结果时应使用的分页类.默认值与 DEFAULT_PAGINATION_CLASS 设置的值相同, 即 'rest_framework.pagination.PageNumberPagination'
    filter_backends     用于过滤查询集的过滤器后端类的列表.默认值与 DEFAULT_FILTER_BACKENDS 设置的值相同

GenericAPIView Methods:
    get_queryset(self)
        应该总是调用 get_queryset() 方法而不是直接访问 queryset 属性, 因为 queryset 只会被计算一起, 这些结果将为后续请求缓存起来.
        该方法可能会被重写以提供动态行为，比如返回基于发出请求的用户的结果集, 例如:
        `
        def get_queryset(self):
            user = self.request.user
            return user.accounts.all()
        `

    get_object(self)
        返回应用于详细视图的对象实例. 默认使用 lookup_field 参数过滤基本的查询集.
        该方法可以被重写以提供更复杂的行为，例如基于多个 URL 参数的对象查找, 例如:
        `
        def get_object(self):
            queryset = self.get_queryset()
            filter = {}
            for field in self.multiple_lookup_fields:
                filter[field] = self.kwargs[field]

            obj = get_object_or_404(queryset, **filter)
            self.check_object_permissions(self.request, obj)  # 如果你的API不包含任何对象级的权限控制，你可以选择不执行这行
            return obj
        `

    filter_queryset(self, queryset)
        给定一个queryset，使用任何过滤器后端进行过滤，返回一个新的queryse, 例如:
        `
        def filter_queryset(self, queryset):
            filter_backends = (CategoryFilter, )

            if 'geo_route' in self.request.query_params:
                filter_backends = (GeoRouteFilter, CategoryFilter)
            elif 'geo_point' in self.request.query_params:
                filter_backends = (GeoPointFilter, CategoryFilter)

            for backend in list(filter_backends):
                queryset = backend().filter_queryset(self.request, queryset, view=self)

            return queryset
        `

    get_serializer_class(self)
        返回应用于序列化的类. 默认为返回 serializer_class 属性的值. 
        可以被重写以提供动态的行为，例如对于读取和写入操作使用不同的序列化器，或者为不同类型的用户提供不同的序列化器. 例如:
        `
        def get_serializer_class(self\):
            if self.request.user.is_staff:
                return FullAccountSerializer
            return BasicAccountSerializer
        `

    其他方法:
        通常并不需要重写以下方法.
        get_serializer_context(self)
            返回包含应该提供给序列化程序的任何额外上下文的字典. 默认包含 'request', 'view' 和 'format' 这些keys. .
        get_serializer(self, instance=None, data=None, many=False, partial=False)
            返回一个序列化器的实例. 
        get_paginated_response(self, data)
            返回分页样式的 Response 对象. 
        paginate_queryset(self, queryset)
            如果需要分页查询，返回页面对象，如果没有为此视图配置分页，则返回 None. 
        filter_queryset(self, queryset)
            给定查询集，使用任何过滤器后端进行过滤，返回一个新的查询集. 

mixins:
    mixins.ListModelMixin
        .list(request, *args, **kwargs) 方法，实现列出结果集.
        如果查询集被填充了数据，则返回 200 OK 响应，将查询集的序列化表示作为响应的主体. 相应数据可以任意分页

    mixins.CreateModelMixin
        .create(request, *args, **kwargs) 方法，实现创建和保存一个新的model实例.
        如果创建了一个对象，这将返回一个 201 Created 响应，将该对象的序列化表示作为响应的主体. 
        如果序列化的表示中包含名为 url的键，则响应的 Location 头将填充该值. 
        如果为创建对象提供的请求数据无效，将返回 400 Bad Request，其中错误详细信息作为响应的正文. 

    mixins.RetrieveModelMixin
        .retrieve(request, *args, **kwargs) 方法，实现返回响应中现有模型的实例.
        如果可以检索对象，则返回 200 OK 响应，将该对象的序列化表示作为响应的主体. 否则将返回 404 Not Found

    mixins.UpdateModelMixin
        .update(request, *args, **kwargs) 方法，实现更新和保存现有模型实例. 
        .partial_update(request, *args, **kwargs) 方法，这个方法和 update 方法类似，但更新的所有字段都是可选的. 这允许支持 HTTP PATCH 请求. 
        如果一个对象被更新，这将返回一个 200 OK 响应，将对象的序列化表示作为响应的主体. 
        如果为更新对象提供的请求数据无效，将返回一个 400 Bad Request 响应，错误详细信息作为响应的正文. 

    mixins.DestroyModelMixin
        .destroy(request, *args, **kwargs) 方法，实现删除现有模型实例. 
        如果删除对象，则返回 204 No Content 响应，否则返回 404 Not Found

钩子函数:
    用于执行创建对象时需要执行的其它方法, 比如发送邮件等功能, 有点类似于 Django 的信号.
    CreateModelMixin.perform_create(serializer)  # 在保存新对象实例时
    UpdateModelMixin.perform_update(serializer)  # 在保存现有对象实例时
    DestroyModelMixin.perform_destroy(instance)  # 在删除对象实例时由
    `
    def perform_create(self, serializer):
        queryset = SignupRequest.objects.filter(user=self.request.user)
        if queryset.exists():
            # 通过抛出 ValidationError() 来提供额外的验证. 当你需要在数据库保存时应用一些验证逻辑时
            raise ValidationError('You have already signed up')  
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        instance = serializer.save()
        # 保存后做一些操作
        send_email_confirmation(user=self.request.user, modified=instance)
    `

创建自定义 mixins. 如果你需要基于 URL conf中的多个字段查找对象，则可以创建一个如下所示的 mixin类：
    class MultipleFieldLookupMixin(object):
        """
        将此 mixin 应用于任何视图或视图集以获得多字段过滤.基于`lookup_fields` 属性，而不是默认的单字段过滤。
        """
        def get_object(self):
            queryset = self.get_queryset()             # 获取基本的queryset
            queryset = self.filter_queryset(queryset)  # 应用任何过滤器后端
            filter = {}
            for field in self.lookup_fields:
                if self.kwargs[field]: # Ignore empty fields.
                    filter[field] = self.kwargs[field]
            return get_object_or_404(queryset, **filter)  # 查找对象

    class RetrieveUserView(MultipleFieldLookupMixin, generics.RetrieveAPIView):
        queryset = User.objects.all()
        serializer_class = UserSerializer
        lookup_fields = ('account', 'username')
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

    # 将request.user 与 author 绑定.调用 create 方法时执行如下函数.
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


# ----------------------------------------------------------------------------
# 通用视图 Generics.* 类 
'''
generics.*:
    generics.ListCreateAPIView 类支持 List、Create 两种视图功能, 分别对应GET和POST请求.
    generics.RetrieveUpdateDestroyAPIView 支持 Retrieve、Update、Destroy 操作, 其对应方法分别是GET、PUT、 PATCH和DELETE.
    generics.RetrieveAPIView        只读 单个模型实例
    generics.CreateAPIView          仅创建
    generics.DestroyAPIView         仅删除单个模型实例
    generics.UpdateAPIView          仅更新单个模型实例
    generics.RetrieveDestroyAPIView 读取或删除 端点以表示 单个模型实例
    generics.ListAPIView            只读 模型实例集合
    generics.RetrieveUpdateAPIView  读取或更新 端点以表示 单个模型实例

    根据实际需求使用, 为你的API写视图时只需要定义queryset和serializer_class即可.
'''

class ArticleListGenericsView(generics.ListCreateAPIView):

    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
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


# ----------------------------------------------------------------------------
# 视图集 ViewSet
'''
视图集
    使用通用视图 generics 类后视图代码已经大大简化,
    但是 ArticleListGenericsView 和 ArticleDetailGenericsView 两个类中 queryset 和 serializer_class 属性依然存在代码重复.
    使用视图集可以将两个类视图进一步合并, 一次性提供 List、Create、Retrieve、Update、Destroy 这5种常见操作,
    这样 queryset 和 seralizer_class 属性也只需定义一次就好, 这就变成了视图集 (viewset).

    ViewSet类与View类几乎相同, 不同之处在于它们提供诸如read或update之类的操作, 而不是get或put等方法处理程序.
    最后一个ViewSet类只绑定到一组方法处理程序, 当它被实例化成一组视图的时候, 通常通过使用一个 Router 类来处理自己定义 URL conf 的复杂性.

viewsets.ViewSet
    ViewSet 类不提供任何操作的实现。为了使用 ViewSet 类，你将重写该类并显式地定义动作实现

viewsets.GenericViewSet

viewsets.ModelViewSet
    必需属性:
        queryset
        serializer_class

viewsets.ReadOnlyModelViewSet
    必需属性:
        queryset
        serializer_class
'''

# viewsets.ModelViewSet: 此视图自动提供`list`, `create`, `retrieve`, `update`和`destroy`操作.
class ArticleViewSet(viewsets.ModelViewSet):

    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)

    # 自行添加, 将request.user与author绑定
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer

    # @action(methods=None, detail:bool=None, url_path=None, url_name=None, **kwargs)
    # 装饰器可用于添加不符合标准 create/update/delete 样式的任何自定义路径.
    # methods:  要响应的请求, 默认 ['get',]
    # detail:   确定此操作是否适用于实例/详细信息请求或集合/列表请求
    # url_path: 默认用 users/<url_path?url_path:函数名>/ 作为URL地址
    # url_name: 默认名称 <basename>-<url_name?url_name:函数名(下划线_替换为-)>, 

    @action(methods=['post'], detail=True, permission_classes=[permissions.IsAdminUser])
    def set_password(self, request):
        '''设置密码'''
        user = self.get_object()
        serializer = PasswordSerializer(data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.data['password'])
            user.save()
            return Response({'status': 'password set'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False)
    def recent_users(self, request):
        '''最近登录用户'''
        recent_users = User.objects.all().order('-last_login')

        page = self.paginate_queryset(recent_users)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(recent_users, many=True)
        return Response(serializer.data)



