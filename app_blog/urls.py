from django.urls import path, include
from app_blog import views
from .feeds import LatestPostsFeed

# 方法1  建议该方法
app_name = 'app_blog'  # 定义应用程序命名空间
urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),   # 使用类视图
    # path('', views.post_list, name='post_list'),  # 使用函数视图
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.post_detail, name='post_detail'),
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
