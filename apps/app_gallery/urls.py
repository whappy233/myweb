from os import name
from django.urls import path, include, re_path
from . import views




# 方法1  建议该方法
app_name = 'app_gallery'  # 定义应用程序命名空间
urlpatterns = [
    path('', views.GalleryListView.as_view(), name='gallery_list'),   # 使用类视图
    path('get_random_background/<int:x>x<int:y>/', views.get_random_background, name='get_random_background'),
    path('detail_ajax/', views.GalleryDetail.as_view(), name='detail_ajax'),
    path('gallery_detail/', views.GalleryDetail.as_view(), name='gallery_detail'),

    path('photo/<int:width>/<int:height>/', views.random_photo, name='photo'),
]
