from os import name
from django.urls import path, include, re_path
from . import views




# 方法1  建议该方法
app_name = 'app_gallery'  # 定义应用程序命名空间
urlpatterns = [
    path('', views.GalleryListView.as_view(), name='gallery_list'),   # 使用类视图
    # path('detail/<int:pk>/<str:slug>/', views.GalleryDetail.as_view(), name='gallery_detail'),
    re_path(r'^detail/(?P<pk>\d+)/(?P<slug>[-\w]+)/$', views.GalleryDetail.as_view(), name='gallery_detail'),
    path('get_random_background/<int:x>x<int:y>/', views.get_random_background, name='get_random_background'),

    path('detail_ajax/', views.ZXX.as_view(), name='detail_ajax'),
]
