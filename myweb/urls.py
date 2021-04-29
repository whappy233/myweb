from django.contrib import admin
from django.urls import path, include, re_path

import xadmin

# 添加网站地图
from django.contrib.sitemaps.views import sitemap
from app_blog.sitemaps import ArticleSitemap

from django.conf import settings
from django.views.static import serve


# 自定义错误处理
# handler400 = ''
# handler403 = 'app_blog.views.permission_denied_view'
# handler404 = 'app_blog.views.page_not_found_view'
# handler500 = 'app_blog.views.server_error_view'


sitemaps = {
    'articles': ArticleSitemap,
    }


# 对应blog/urls 中的方法1
urlpatterns = [
    path('admin/', admin.site.urls),
    path('xadmin/', xadmin.site.urls),
    path('', include('app_blog.urls', namespace='app_blog')),
    path('', include('app_comments.urls', namespace='app_comments')),
    path('user/', include('app_user.urls', namespace='app_uesr')),
    path('gallery/', include('app_gallery.urls', namespace='app_gallery')),

    re_path(r'^media/(?P<path>.*)', serve, {'document_root': settings.MEDIA_ROOT}),  # 媒体文件
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),  # 静态文件

    # path('ckeditor/', include('ckeditor_uploader.urls')),
    path('mdeditor/', include('mdeditor.urls')),  # mdeditor 富文本上传图片

    path('sitemap.xml', sitemap, {'sitemaps':sitemaps}, name='django.contrib.sitemaps.views.sitemap'),  # 网站地图

] # + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




'''

info = self.model._meta.app_label, self.model._meta.model_name
urlpatterns = [
    path('', wrap(self.changelist_view), name='%s_%s_changelist' % info),
    path('add/', wrap(self.add_view), name='%s_%s_add' % info),
    path('autocomplete/', wrap(self.autocomplete_view), name='%s_%s_autocomplete' % info),
    path('<path:object_id>/history/', wrap(self.history_view), name='%s_%s_history' % info),
    path('<path:object_id>/delete/', wrap(self.delete_view), name='%s_%s_delete' % info),
    path('<path:object_id>/change/', wrap(self.change_view), name='%s_%s_change' % info),
    # For backwards compatibility (was the change url before 1.9)
    path('<path:object_id>/', wrap(RedirectView.as_view(
        pattern_name='%s:%s_%s_change' % ((self.admin_site.name,) + info)
    ))),

'''