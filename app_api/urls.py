from django.urls import re_path, path
from rest_framework.urlpatterns import format_suffix_patterns


from . import views


app_name = 'app_api'
urlpatterns = [
    # 函数视图
    # re_path(r'^articles/$', views.article_list),
    # re_path(r'^articles/(?P<pk>[0-9]+)$', views.article_detail),
    re_path(r'^$', views.api_root, name='root'),

    # 类视图
    re_path(r'^users/$', views.UserList.as_view(), name='users-list'),
    re_path(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view(), name='user-detail'),

    re_path(r'^profile/$', views.UserProfileList.as_view(), name='userprofiles-list'),
    re_path(r'^profile/(?P<pk>[0-9]+)/$', views.UserProfileDetail.as_view(), name='userprofile-detail'),

    re_path(r'^articles/$', views.ArticleList.as_view(), name='articles-list'),
    # re_path(r'^articles/(?P<pk>[0-9]+)/$', views.ArticleDetail.as_view(), name='article-detail'),
    path('articles/<int:pk>/', views.ArticleDetail.as_view(), name='article-detail'),



]

urlpatterns = format_suffix_patterns(urlpatterns)


# 视图集. 一个视图集对应了 List、Create、Retrieve、Update、Destroy 五种操作.
# from rest_framework.routers import DefaultRouter

# router = DefaultRouter()
# router.register(r'articles', viewset=views.ArticleViewSet)
# urlpatterns += router.urls


# 视图集指定方法映射(指定需要的操作)
# article_list = views.ArticleViewSet.as_view({
#     'get': 'list',
#     'post': 'create'
# })

# article_detail = views.ArticleViewSet.as_view({
#     'get': 'retrieve',  # 只处理get请求，获取单个记录
# })

# urlpatterns = [
#     re_path(r'^articles/$', article_list),
#     re_path(r'^articles/(?P<pk>[0-9]+)/$', article_detail),
# ]

# urlpatterns = format_suffix_patterns(urlpatterns)
