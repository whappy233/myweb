from django.urls import include, path, re_path

from . import views
from .search_views import MySearchView
from .feeds import LatestArticlesFeed



app_name = 'app_blog'  # 定义应用程序命名空间
urlpatterns = [
    path('', views.IndexView.as_view(), name='article_list'),       # 使用类视图
    path('authors/<str:author_name>/', views.AuthorDetailView.as_view(), name='article_list_by_author'),  # 某个作者下的所有文章
    path('categorys/<slug:category_slug>/', views.CategoryDetailView.as_view(), name='category_detail'),  # 分组下的文章列表
    re_path(r'^tags/(?P<tag_slug>[-\w]+)/$', views.TagDetailView.as_view(), name='article_list_by_tag'),  # 某个标签下的所有文章

    path('details/<slug:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),     # 文章详情

    path('<int:article_id>/share/', views.article_share, name='article_share'),                 # 分享文章

    path('se/', MySearchView(), name='haystack_search'),         # 搜索

    path('feed/', LatestArticlesFeed(), name='article_feed'),       # 订阅链接

    path('ajax_app_test/', views.ajax_test, name='ajax_app_test'),  # ajax 请求
    path('blog/like/', views.blog_like, name='blog_like'),          # 点赞 +1 (ajax)
    path('refresh/', views.refresh_memcache, name='refresh'),       # 刷新(清空) Redis缓存

]


from rest_framework.routers import DefaultRouter
from .views import ContentSearchViewSet

router = DefaultRouter()
router.register(r"search", ContentSearchViewSet, basename="sea")
urlpatterns += router.urls
