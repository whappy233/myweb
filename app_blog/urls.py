from django.urls import include, path, re_path

from app_blog import views

from .feeds import LatestArticlesFeed



app_name = 'app_blog'  # 定义应用程序命名空间
urlpatterns = [
    path('', views.ArticleListView.as_view(), name='article_list'),   # 使用类视图
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),  # 分组下的文章列表
    path('detail/<int:year>/<int:month>/<int:day>/<slug:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),  # 文章详情

    path('archive/<int:year>/<int:month>/', views.month_archive, name='month_archive'),  #  月度归档 (某月的列表)

    path('<int:article_id>/share/', views.article_share, name='article_share'),  # 分享文章
    path('author/<str:author_name>', views.article_list, name='article_list_by_author'),  # 某个作者下的所有文章

    re_path(r'^tags/(?P<tag_slug>[-\w]+)/$', views.article_list, name='article_list_by_tag'),  # 某个标签下的所有文章

    path('search/', views.article_search, name='article_search'),   # 搜索
    path('feed/', LatestArticlesFeed(), name='article_feed'),  # 订阅链接

    path('ajax_app_test/', views.ajax_test, name='ajax_app_test'),  # ajax 请求
    path('blog/like/', views.blog_like, name='blog_like'),  # 点赞 +1 (ajax)

]


