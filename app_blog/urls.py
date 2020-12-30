from django.urls import path, include, re_path
from app_blog import views
from .feeds import LatestPostsFeed

app_name = 'app_blog'  # 定义应用程序命名空间
urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),   # 使用类视图
    # path('', views.post_list, name='post_list'),  # 使用函数视图
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.post_detail, name='post_detail'),
    path('<int:post_id>/share/', views.post_share, name='post_share'),
    path('author/<str:author_name>', views.post_list, name='post_list_by_author'),
    path('tags/<slug:tag_slug>', views.post_list, name='post_list_by_tag'),
    path('search/', views.post_search, name='post_search'),
    path('feed/', LatestPostsFeed(), name='post_feed'),
    path('ajax_app_test/', views.ajax_test, name='ajax_app_test'),

    path('post/admin/', views.AdminPostListView.as_view(), name='admin_pub_post_list'),
    path('post/admin/draft', views.AdminPostListView.as_view(), {'show_publish': False}, name='admin_drafy_post_list'),
    # path('post/admin/chnage/<int:year>/<int:month>/<int:day>/<slug:post>/', views.AdminPublishedPostListView.as_view(), name='admin_post_list'),
]


# urlpatterns = [
#     # 所有文章列表 - 不需登录
#     path('', views.PostListView.as_view(), name='post_list'),

#     # 展示文章详情 - 登录/未登录均可
#     path(r'post/<int:year>/<int:month>/<int:day>/<slug:post>/', views.PostDetailView.as_view(), name='post_detail'),

#     # 草稿箱 - 需要登录
#     path('draft/', views.PostDraftListView.as_view(), name='post_draft_list'),

#     # 已发表文章列表(含编辑) - 需要登录
#     path('admin/', views.PublishedPostListView.as_view(), name='published_post_list'),

#     # 更新文章- 需要登录
#     re_path(r'^post/(?P<pk>\d+)/(?P<slug1>[-\w]+)/update/$', views.PostUpdateView.as_view(), name='post_update'),
#     # 创建文章 - 需要登录
#     re_path(r'^post/create/$', views.PostCreateView.as_view(), name='post_create'),

#     # 发表文章 - 需要登录
#     re_path(r'^post/(?P<pk>\d+)/(?P<slug1>[-\w]+)/publish/$', views.post_publish, name='post_publish'),

#     # 删除文章 - 需要登录
#     re_path(r'^post/(?P<pk>\d+)/(?P<slug1>[-\w]+)/delete$', views.PostDeleteView.as_view(), name='post_delete'),

#     # 展示类别列表
#     # re_path(r'^category/$', views.CategoryListView.as_view(), name='category_list'),

#     # 展示类别详情
#     # re_path(r'^category/(?P<slug>[-\w]+)/$', views.CategoryDetailView.as_view(), name='category_detail'),

#     # 展示Tag详情
#     # re_path(r'^tags/(?P<slug>[-\w]+)/$', views.TagDetailView.as_view(), name='tag_detail'),

#     # 搜索文章
#     re_path(r'^search/$', views.post_search, name='post_search'),

# ]
