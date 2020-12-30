from django.urls import path, include, re_path
from app_blog import views
from .feeds import LatestPostsFeed

# 方法1  建议该方法
app_name = 'app_blog'  # 定义应用程序命名空间
urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),   # 使用类视图
    # path('', views.post_list, name='post_list'),  # 使用函数视图
    path('<int:year>/<int:month>/<int:day>/<slug:post>/',
         views.post_detail, name='post_detail'),
    path('<int:post_id>/share/', views.post_share, name='post_share'),
    path('feed/', LatestPostsFeed(), name='post_feed'),
    path('author/<str:author_name>', views.post_list, name='post_list_by_author'),
    path('tags/<slug:tag_slug>', views.post_list, name='post_list_by_tag'),
    path('search/', views.post_search, name='post_search'),
    path('ajax_app_test/', views.ajax_test, name='ajax_app_test'),
]

# 方法2
# extra_urls = [
#     path('',views.post_list, name='post_list'),
#     path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.post_datail, name='post_datail'),]
# urlpatterns = [path('', include(extra_urls))]


# urlpatterns = [
#     # 所有文章列表 - 不需登录
#     path('', views.ArticleListView.as_view(), name='article_list'),

#     # 展示文章详情 - 登录/未登录均可
#     re_path(r'^article/(?P<pk>\d+)/(?P<slug1>[-\w]+)/$', views.ArticleDetailView.as_view(), name='article_detail'),

#     # 草稿箱 - 需要登录
#     path('draft/', views.ArticleDraftListView.as_view(), name='article_draft_list'),

#     # 已发表文章列表(含编辑) - 需要登录
#     path('admin/', views.PublishedArticleListView.as_view(), name='published_article_list'),

#     # 更新文章- 需要登录
#     re_path(r'^article/(?P<pk>\d+)/(?P<slug1>[-\w]+)/update/$', views.ArticleUpdateView.as_view(), name='article_update'),
#     # 创建文章 - 需要登录
#     re_path(r'^article/create/$', views.ArticleCreateView.as_view(), name='article_create'),

#     # 发表文章 - 需要登录
#     re_path(r'^article/(?P<pk>\d+)/(?P<slug1>[-\w]+)/publish/$', views.article_publish, name='article_publish'),

#     # 删除文章 - 需要登录
#     re_path(r'^article/(?P<pk>\d+)/(?P<slug1>[-\w]+)/delete$', views.ArticleDeleteView.as_view(), name='article_delete'),

#     # 展示类别列表
#     re_path(r'^category/$', views.CategoryListView.as_view(), name='category_list'),

#     # 展示类别详情
#     re_path(r'^category/(?P<slug>[-\w]+)/$', views.CategoryDetailView.as_view(), name='category_detail'),

#     # 展示Tag详情
#     re_path(r'^tags/(?P<slug>[-\w]+)/$', views.TagDetailView.as_view(), name='tag_detail'),

#     # 搜索文章
#     re_path(r'^search/$', views.article_search, name='article_search'),

# ]
