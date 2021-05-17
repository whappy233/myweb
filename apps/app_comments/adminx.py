from django.urls import reverse
from django.utils.html import format_html
from xadmin.sites import register

from .models import Comments, Wanderer


@register(Comments)
class CommentAdmin:
    # 显示字段
    list_display = ['id', 'body', 'link_to_UserInfo', 
                    'link_to_WandererInfo', 'parent_comment',
                    'link_to_article', 'created_time', 'is_visible']
    # 搜索字段
    search_fields = ['body']  
    # 过滤器
    list_filter = ['created_time', 'is_visible', 'object_id', 'content_type']  
    list_editable = ['is_visible']
    actions = ['disable_commentstatus', 'enable_commentstatus']
    # 可点击的项
    list_display_links = ('body',)  
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
    def link_to_UserInfo(self, obj):
        info = (obj.author._meta.app_label, obj.author._meta.model_name)
        link = reverse('xadmin:%s_%s_change' % info, args=(obj.author.id,))
        return format_html(f'<a href="{link}">{obj.author.username}</a>')
    link_to_UserInfo.short_description = '用户'

    # admin/accounts/bloguser/2/change/
    # 链接到用户信息
    def link_to_WandererInfo(self, obj):
        info = (obj.wanderer._meta.app_label, obj.wanderer._meta.model_name)
        link = reverse('xadmin:%s_%s_change' % info, args=(obj.wanderer.id,))
        return format_html(f'<a href="{link}">{obj.wanderer.username}</a>')
    link_to_WandererInfo.short_description = '散人'

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


    # def save_models(self):
    #     request = self.request
    #     obj  = self.new_obj
    #     form = self.form_obj



@register(Wanderer)
class WandererAdmin:
    list_display = ['id', 'username', 'email', 'created_time']  # 显示字段
    search_fields = ['username', 'email']  # 搜索字段
    list_filter = ['created_time']  # 过滤器
    list_display_links = ('username',)  # 可点击的项