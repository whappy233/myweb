from django.urls import reverse
from django.utils.html import format_html
from xadmin.sites import register
from .models import Comments, MpComments


class ActionMixIn:
    actions = ['enable_commentstatus', 'disable_commentstatus', 'enable_overhead', 'disable_overhead']

    def enable_commentstatus(self, request, queryset):
        '''显示评论'''
        queryset.update(is_hide=False)
    enable_commentstatus.short_description = '显示评论'

    def disable_commentstatus(self, request, queryset):
        '''隐藏评论'''
        queryset.update(is_hide=True)
    disable_commentstatus.short_description = '隐藏评论'

    def enable_overhead(self, request, queryset):
        '''顶置评论'''
        queryset.update(is_overhead=True)
    enable_overhead.short_description = '顶置评论'

    def disable_overhead(self, request, queryset):
        '''取消顶置'''
        queryset.update(is_overhead=False)
    disable_overhead.short_description = '取消顶置'


@register(Comments)
class CommentAdmin(ActionMixIn):
    # 显示字段
    list_display = ['id', 'link_to_uuid', 'link_to_body', 'parent_comment',
                    'link_to_commenter',
                    'content_type', 'link_to_article',
                    'created_time', 'is_overhead', 'is_hide']
    # 搜索字段
    search_fields = ['body']  
    # 过滤器
    list_filter = ['created_time', 'is_overhead', 'is_hide', 'object_id', 'content_type', 'parent_comment']  
    list_editable = ['is_overhead', 'is_hide']
    # 可点击的项
    list_display_links = ('link_to_body', 'link_to_uuid')

    # admin/accounts/bloguser/2/change/
    # 链接到用户信息
    def link_to_commenter(self, obj):
        info = (obj.author._meta.app_label, obj.author._meta.model_name)
        link = reverse('xadmin:%s_%s_change' % info, args=(obj.author.id,))
        return format_html(f'<a href="{link}">{obj.author.username}</a>')
    link_to_commenter.short_description = '评论作者'

    # admin/blog/article/1/change/
    # 链接到关联对象
    def link_to_article(self, obj):
        c_id = obj.object_id
        c_obj = obj.content_object

        info = (c_obj._meta.app_label, c_obj._meta.model_name)
        link = reverse('xadmin:%s_%s_change' % info, args=(c_obj.id,))
        text = f'(ID: {c_id}) {c_obj.title}'
        return format_html(f'<a href="{link}">{text}</a>')
    link_to_article.short_description = '关联对象详情'

    def link_to_uuid(self, obj):
        uuid = obj.uuid
        return format_html(f'{uuid[:5]}... <a href="#" title="点击复制" onclick="copytext(`{uuid}`)">🔖</a>')
    link_to_uuid.short_description = 'uuid'

    def link_to_body(self, obj):
        return f'{obj.body[:10]}...'
    link_to_body.short_description = '评论内容'


@register(MpComments)
class MpCommentsAdmin(ActionMixIn):
    # 显示字段
    list_display = ['id', 'link_to_uuid', 'body', 'parent_comment', 
                    'link_to_commenter', 'content_type', 'link_to_article',
                    'created_time',
                    'level', 'lft', 'rght', 'tree_id', 'is_overhead', 'is_hide']
    # 搜索字段
    search_fields = ['body']  
    # 过滤器
    list_filter = ['is_overhead', 'is_hide', 'object_id', 'content_type', 'parent_comment']  
    list_editable = ['is_overhead', 'is_hide']
    # 可点击的项
    list_display_links = ('body', 'link_to_uuid')

    # admin/accounts/bloguser/2/change/
    # 链接到用户信息
    def link_to_commenter(self, obj):
        info = (obj.author._meta.app_label, obj.author._meta.model_name)
        link = reverse('xadmin:%s_%s_change' % info, args=(obj.author.id,))
        return format_html(f'<a href="{link}">{obj.author.username}</a>')
    link_to_commenter.short_description = '评论作者'

    # admin/blog/article/1/change/
    # 链接到关联对象
    def link_to_article(self, obj):
        c_id = obj.object_id
        c_obj = obj.content_object

        info = (c_obj._meta.app_label, c_obj._meta.model_name)
        link = reverse('xadmin:%s_%s_change' % info, args=(c_obj.id,))
        text = f'(ID: {c_id}) {c_obj.title}'
        return format_html(f'<a href="{link}">{text}</a>')
    link_to_article.short_description = '关联对象详情'

    def link_to_uuid(self, obj):
        uuid = obj.uuid
        return format_html(f'{uuid[:5]}...<a href="#" title="点击复制" onclick="copytext(`{uuid}`)">🔖</a>')
    link_to_uuid.short_description = 'uuid'

    def link_to_body(self, obj):
        return f'{obj.body[:10]}...'
    link_to_body.short_description = '评论内容'
