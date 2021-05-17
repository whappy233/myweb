from django.urls import reverse
from django.utils.html import format_html
from xadmin.sites import register

from .models import Comments


@register(Comments)
class CommentAdmin:
    list_display = ['id', 'body', 'link_to_userinfo', 'parent_comment',
                    'link_to_article', 'created_time', 'is_visible']  # 显示字段
    search_fields = ['body']  # 搜索字段
    list_filter = ['created_time', 'is_visible', 'object_id', 'content_type']  # 过滤器
    list_editable = ['is_visible']
    actions = ['disable_commentstatus', 'enable_commentstatus']
    list_display_links = ('body',)  # 可点击的项
    # raw_id_fields = ['article',]  # 下拉框改为微件

    def disable_commentstatus(self, request, queryset):
        '''隐藏评论'''
        queryset.update(is_visible=False)
    disable_commentstatus.short_description = '隐藏评论'

    def enable_commentstatus(self, request, queryset):
        '''显示评论'''
        queryset.update(is_visible=True)
    enable_commentstatus.short_description = '显示评论'

    # admin/accounts/bloguser/2/change/
    # 链接到用户信息
    def link_to_userinfo(self, obj):
        info = (obj.author._meta.app_label, obj.author._meta.model_name)
        link = reverse('xadmin:%s_%s_change' % info, args=(obj.author.id,))
        return format_html(f'<a href="{link}">{obj.author.username}</a>')
    link_to_userinfo.short_description = '用户'

    # admin/blog/article/1/change/
    # 链接到关联对象
    def link_to_article(self, obj):
        c_type = obj.content_type
        c_id = obj.object_id
        c_obj = obj.content_object

        info = (c_obj._meta.app_label, c_obj._meta.model_name)
        link = reverse('xadmin:%s_%s_change' % info, args=(c_obj.id,))
        text = f'({c_type}: {c_id}) {c_obj.title}'
        return format_html(f'<a href="{link}">{text}</a>')
    link_to_article.short_description = '关联对象详情'
