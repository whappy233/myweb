import xadmin
from django.urls import reverse
from django.utils.html import format_html

from .models import Comments


class CommentAdmin:
    list_display = ['id', 'body', 'link_to_userinfo', 'parent_comment', 'link_to_article', 'created_time', 'is_active']  # 显示字段
    search_fields = ['author', 'body', 'content_object']  # 搜索字段
    list_filter = ['created_time', 'is_active']  # 过滤器
    list_editable = ['is_active']
    actions = ['disable_commentstatus', 'enable_commentstatus']
    list_display_links = ('body',) # 可点击的项
    # raw_id_fields = ['article',]  # 下拉框改为微件

    def disable_commentstatus(self, request, queryset):
        '''禁用评论'''
        queryset.update(is_active=False)
    disable_commentstatus.short_description = '禁用评论'

    def enable_commentstatus(self, request, queryset):
        '''启用评论'''
        queryset.update(is_active=True)
    enable_commentstatus.short_description = '启用评论'

    # admin/accounts/bloguser/2/change/
    # 链接到用户信息
    def link_to_userinfo(self, obj):
        info = (obj.author._meta.app_label, obj.author._meta.model_name)
        link = reverse('admin:%s_%s_change' % info, args=(obj.author.id,))
        return format_html(u'<a href="%s">%s</a>' %(link, obj.author.username))
    link_to_userinfo.short_description = '用户'

    # admin/blog/article/1/change/
    # 链接到关联对象
    def link_to_article(self, obj):
        info = (obj.content_object._meta.app_label, obj.content_object._meta.model_name)
        link = reverse('admin:%s_%s_change' % info, args=(obj.content_object.id,))
        text= f'({"/".join(info)}: {obj.content_object.id}) {obj.content_object.title}'
        return format_html(u'<a href="%s">%s</a>' % (link, text))
    link_to_article.short_description = '关联对象详情'
xadmin.site.register(Comments, CommentAdmin)
