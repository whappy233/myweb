from django.contrib import admin
from django.urls import path, include, re_path

# 添加网站地图
from django.contrib.sitemaps.views import sitemap
from app_blog.sitemaps import PostSitemap

from django.conf import settings
from django.views.static import serve


# 对应blog/urls 中的方法1
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app_blog.urls', namespace='app_blog')),
    path('user/', include('app_user.urls', namespace='app_uesr')),
    path('sheet/', include('app_sheet.urls', namespace='app_sheet')),
    path('gallery/', include('app_gallery.urls', namespace='app_gallery')),

    re_path(r'^media/(?P<path>.*)', serve, {'document_root': settings.MEDIA_ROOT}),  # 媒体文件
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),  # 静态文件

    path('sitemap.xml', sitemap, {'sitemaps':{'posts':PostSitemap}}, name='django.contrib.sitemaps.views.sitemap'),  # 网站地图
]

