from django.urls import reverse
from django.utils.html import format_html
from xadmin.sites import register
from .models import Comments, Wanderer, MpComments


@register(Comments)
class CommentAdmin:
    # 显示字段
    list_display = ['id', 'link_to_uuid', 'link_to_body', 'parent_comment',
                    'link_to_commenter',
                    'content_type', 'link_to_article',
                    'last_mod_time', 'is_overhead', 'is_hide']
    # 搜索字段
    search_fields = ['body']  
    # 过滤器
    list_filter = ['last_mod_time', 'is_overhead', 'is_hide', 'object_id', 'content_type', 'parent_comment']  
    list_editable = ['is_overhead', 'is_hide']
    actions = ['enable_commentstatus', 'disable_commentstatus', 'enable_overhead', 'disable_overhead']
    # 可点击的项
    list_display_links = ('link_to_body', 'link_to_uuid')

    # 当 user 和 wanderer 同时存在时, 清除 wanderer 
    # def save_models(self):
    #     if self.new_obj.author and self.new_obj.wanderer:
    #         self.new_obj.wanderer = None
    #     super().save_models()

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


    # admin/accounts/bloguser/2/change/
    # admin/accounts/bloguser/2/change/
    # 链接到用户信息
    def link_to_commenter(self, obj):
        t1 = t2 = '-'
        if obj.author:
            info = (obj.author._meta.app_label, obj.author._meta.model_name)
            link = reverse('xadmin:%s_%s_change' % info, args=(obj.author.id,))
            t1 = f'<a href="{link}">{obj.author.username}</a>'
        if obj.wanderer:
            info = (obj.wanderer._meta.app_label, obj.wanderer._meta.model_name)
            link = reverse('xadmin:%s_%s_change' % info, args=(obj.wanderer.id,))
            t2 = f'<a href="{link}">{obj.wanderer.username}</a>'
        return format_html(f'{t1} / {t2}')
    link_to_commenter.short_description = 'User/Wanderer'

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


@register(Wanderer)
class WandererAdmin:
    list_display = ['id', 'username', 'email', 'created_time']  # 显示字段
    search_fields = ['username', 'email']  # 搜索字段
    list_filter = ['created_time']  # 过滤器
    list_display_links = ('username',)  # 可点击的项
    # list_editable = ['username']


@register(MpComments)
class MpCommentsAdmin:
    # 显示字段
    list_display = ['id', 'link_to_uuid', 'link_to_body', 'parent', 
                    'link_to_commenter', 'content_type', 'link_to_article',
                    'created_time',
                    'level', 'lft', 'rght', 'tree_id', 'is_overhead', 'is_hide']
    # 搜索字段
    search_fields = ['body']  
    # 过滤器
    list_filter = ['is_overhead', 'is_hide', 'object_id', 'content_type', 'parent']  
    list_editable = ['is_overhead', 'is_hide']
    actions = ['enable_commentstatus', 'disable_commentstatus', 'enable_overhead', 'disable_overhead']
    # 可点击的项
    list_display_links = ('link_to_body', 'link_to_uuid')

    # 当 user 和 wanderer 同时存在时, 清除 wanderer 
    # def save_models(self):
    #     if self.new_obj.author and self.new_obj.wanderer:
    #         self.new_obj.wanderer = None
    #     super().save_models()

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


    # admin/accounts/bloguser/2/change/
    # admin/accounts/bloguser/2/change/
    # 链接到用户信息
    def link_to_commenter(self, obj):
        t1 = t2 = '-'
        if obj.author:
            info = (obj.author._meta.app_label, obj.author._meta.model_name)
            link = reverse('xadmin:%s_%s_change' % info, args=(obj.author.id,))
            t1 = f'<a href="{link}">{obj.author.username}</a>'
        if obj.wanderer:
            info = (obj.wanderer._meta.app_label, obj.wanderer._meta.model_name)
            link = reverse('xadmin:%s_%s_change' % info, args=(obj.wanderer.id,))
            t2 = f'<a href="{link}">{obj.wanderer.username}</a>'
        return format_html(f'{t1} / {t2}')
    link_to_commenter.short_description = 'User/Wanderer'

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
