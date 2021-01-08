from django.urls import path, include, re_path
from app_blog import views
from .feeds import LatestPostsFeed

app_name = 'app_blog'  # 定义应用程序命名空间
urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),   # 使用类视图
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),  # 分组下的文章列表

    path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.post_detail, name='post_detail'),  # 文章详情

    path('<int:post_id>/share/', views.post_share, name='post_share'),  # 分享文章
    path('author/<str:author_name>', views.post_list, name='post_list_by_author'),  # 某个作者下的所有文章
    path('tags/<slug:tag_slug>', views.post_list, name='post_list_by_tag'),  # 某个标签下的所有文章
    path('search/', views.post_search, name='post_search'),   # 搜索
    path('feed/', LatestPostsFeed(), name='post_feed'),  # 订阅链接

    path('ajax_app_test/', views.ajax_test, name='ajax_app_test'),  # ajax 请求
    path('blog/like/', views.blog_like, name='blog_like'),  # 点赞 +1 (ajax)

]


