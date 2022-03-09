'''
给URL添加可选的格式后缀:
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


from app_api.views import UserViewSet1
from django.urls import re_path, path, include
from .views import ArticleListAPIView, ArticleDetailAPIView, ArticleViewSet, UserViewSet
from rest_framework import renderers, routers


urlpatterns = [
    # 函数视图
    path('articles/', article_list),
    path('articles/<int:pk>/', article_detail),

    # APIView 类视图
    path('articles/', ArticleListAPIView.as_view()),
    path('articles/<int:pk>/', ArticleDetailAPIView.as_view()),
]

# 在使用类视图时或视图集时, 添加:
from rest_framework.urlpatterns import format_suffix_patterns
urlpatterns = format_suffix_patterns(urlpatterns)


# --------------------------------------------------------------------------
# 视图集路由
# --------------------------------------------------------------------------

'''
routers.SimpleRouter
    该路由器包括标准集合list, create, retrieve, update, partial_update 和 destroy 动作的路由.
    视图集中还可以使用 @action 装饰器标记要被路由的其他方法.
    默认情况下, 由SimpleRouter创建的URL将附加尾部斜杠,在实例化路由器时,可以通过将 trailing_slash 参数设置为`False'来修改此行为
    router = SimpleRouter(trailing_slash=False)

    路由器将匹配包含除斜杠和句点字符以外的任何字符的查找值.对于更严格（或更宽松）的查找模式, 
    请在视图集上设置lookup_value_regex属性.例如, 你可以将查找限制为有效的UUID：
    class MyModelViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
        lookup_field = 'my_model_id'
        lookup_value_regex = '[0-9a-f]{32}'

    # URL样式	                             HTTP方法	              动作	                URL 名
    --------------------------------------------------------------------------------------------------------
    # {prefix}/	                               GET	                 list	           {basename}-list
    #                                          POST	                 create
    --------------------------------------------------------------------------------------------------------
    # {prefix}/{methodname}/	      由 @action methods 参数定义	   @action	         {basename}-{methodname}
    --------------------------------------------------------------------------------------------------------
    # {prefix}/{lookup}/	                   GET	                 retrieve	        {basename}-detail
    #                                          PUT	                 update
    #                                          PATCH	             partial_update
    #                                          DELETE	             destroy
    --------------------------------------------------------------------------------------------------------
    # {prefix}/{lookup}/{methodname}/	由 @action methods 参数定义    @action            {basename}-{methodname}
    --------------------------------------------------------------------------------------------------------

routers.DefaultRouter
    类似于上面的 SimpleRouter, 但是还包括一个默认返回所有列表视图的超链接的API根视图.它还生成可选的.json样式格式后缀的路由.
    以通过将 trailing_slash 参数设置为`False'来删除URL路由的尾部斜杠.
    router = DefaultRouter(trailing_slash=False)

    # URL样式	                             HTTP方法	              动作	                URL名称
    --------------------------------------------------------------------------------------------------------
    # [.format]	                               GET	                自动生成的root url	    api-root
    --------------------------------------------------------------------------------------------------------
    # {prefix}/[.format]	                   GET	                 list	            {basename}-list
    #                                          POST	                 create
    --------------------------------------------------------------------------------------------------------
    # {prefix}/{methodname}/[.format]	 由 @action methods 参数定义   @action	         {basename}-{methodname}
    --------------------------------------------------------------------------------------------------------
    # {prefix}/{lookup}/[.format]	           GET	                 retrieve	        {basename}-detail
    #                                          PUT	                 update
    #                                          PATCH	             partial_update
    #                                          DELETE	             destroy
    --------------------------------------------------------------------------------------------------------
    # {prefix}/{lookup}/{methodname}/[.format]  由 @action methods 参数定义    @action    {basename}-{methodname}
    --------------------------------------------------------------------------------------------------------

routers:
    router = routers.SimpleRouter()
    router.register(r'users', UserViewSet)
    router.register(r'articles', ArticleViewSet, basename='basename')

    # urlpatterns = router.urls
    # urlpatterns += router.urls
    urlpatterns = [
        ...
        url(r'^api/', include(router.urls, namespace='api')),
    ]

    NOTE:
    # .register(prefix, viewset, basename=None)
    # prefix      用于此组路由的URL前缀. 
    # viewset     处理请求的viewset类. 
    # basename    用于创建的URL名称的基本名称.
    #             如果不设置该参数, 将根据视图集的queryset属性（如果有）来自动生成基本名称<model_name>. 
    #             注意, 如果视图集不包括queryset属性, 那么在注册视图集时必须设置 basename

    # 上面的示例将生成以下URL模式：
    #     URL pattern: ^users/$           Name: 'user-list'
    #     URL pattern: ^users/{pk}/$      Name: 'user-detail'
    #     URL pattern: ^articles/$        Name: 'basename-list'
    #     URL pattern: ^articles/{pk}/$   Name: 'basename-detail'
    #     URL pattern: ^articles/{pk}/$   Name: 'basename-detail'

    对于定义在 UserViewSet 中的 @action, 将会自动生成 URL:
    URL pattern: ^users/<url_path?url_path:函数名>/$       Name: 'user-<url_name?url_name:函数名(下划线_替换为-)>'
    URL pattern: ^users/{pk}/<url_path?url_path:函数名>/$  Name: 'user-<url_name?url_name:函数名(下划线_替换为-)>'
'''

# 自定义 Routers
from rest_framework.routers import Route, DynamicRoute, SimpleRouter
class CustomReadOnlyRouter(SimpleRouter):
    """
    A router for read-only APIs, which doesn't use trailing slashes.
    """
    routes = [
        Route(
            url=r'^{prefix}$',              # 表示要路由的URL的字符串.可能包括以下格式字符串: 
                                            # {prefix} - 用于此组路由的URL前缀.
                                            # {lookup} - 用于与单个实例进行匹配的查找字段.
                                            # {trailing_slash} - 可以是一个'/'或一个空字符串, 这取决于trailing_slash参数.

            mapping={'get': 'list'},        # HTTP方法名称到视图方法的映射

            name='{basename}-list',         # 在reverse调用中使用的URL的名称.可能包括以下格式字符串:
                                            # {basename} - 用于创建的URL名称的基本名称

            initkwargs={'suffix': 'List'}   # 实例化视图时应传递的任何其他参数的字典.注意，suffix参数被保留用于标识视图集类型，在生成视图名称和面包屑链接时使用
        ),
        Route(
            url=r'^{prefix}/{lookup}$',
            mapping={'get': 'retrieve'},
            name='{basename}-detail',
            initkwargs={'suffix': 'Detail'}
        ),
        DynamicRoute(
            url=r'^{prefix}/{lookup}/{methodnamehyphen}$',  # 表示要路由的URL的字符串.可以包括与"Route"相同的格式字符串，并且另外接受
                                                            # 并且另外接受 {methodname} 和 {methodnamehyphen} 格式字符串

            name='{basename}-{methodnamehyphen}',           # 在reverse调用中使用的URL的名称.
                                                            # 可能包括以下格式字符串：{basename}，{methodname}和{methodnamehyphen}

            initkwargs={}                                   # 实例化视图时应传递的任何其他参数的字典
        )
    ]







# 创建路由器并注册我们的视图. 
router = routers.DefaultRouter()  # DefaultRouter 类会自动创建API根视图
router.register(r'articles', ArticleViewSet)
router.register(r'users', UserViewSet)


urlpatterns = [
    re_path(r'^xxx', include(router.urls)),
]



# 你也可以明确地将ViewSets绑定到URL 视图集指定方法映射(指定需要的操作)
article_list = ArticleViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

article_detail = ArticleViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

user_list = UserViewSet.as_view({'get': 'list'})
recent_users = UserViewSet.as_view({'get': 'recent_users'})

user_detail = UserViewSet.as_view({'get': 'retrieve'})
set_password = UserViewSet.as_view({'post': 'set_password'})

urlpatterns = format_suffix_patterns([

    re_path(r'^articles/$', article_list, name='article-list'),
    re_path(r'^articles/(?P<pk>[0-9]+)/$', article_detail, name='article-detail'),
    re_path(r'^users/$', user_list, name='user-list'),
    re_path(r'^recent_users/$', recent_users, name='recent_users'),
    re_path(r'^users/(?P<pk>[0-9]+)/$', user_detail, name='user-detail'),
    re_path(r'^articles/(?P<pk>[0-9]+)/set_password/$', set_password, name='set_password'),
])




