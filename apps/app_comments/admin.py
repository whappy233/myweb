from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Comments, MpComments
from mptt.admin import DraggableMPTTAdmin

# admin.site.register(Comments)  # 注册方式1
@admin.register(Comments)  # 注册方式2（使用包装）
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'body', 'link_to_userinfo', 'parent_comment', 'link_to_article', 'created_time', 'is_hide']  # 显示字段
    search_fields = ['author', 'body', 'content_object']  # 搜索字段
    list_filter = ['created_time', 'is_hide']  # 过滤器
    list_editable = ['is_hide']
    actions = ['disable_commentstatus', 'enable_commentstatus']
    list_display_links = ('body',) # 可点击的项
    # raw_id_fields = ['article',]  # 下拉框改为微件


    def disable_commentstatus(self, request, queryset):
        '''隐藏评论'''
        queryset.update(is_hide=True)
    disable_commentstatus.short_description = '隐藏评论'

    def enable_commentstatus(self, request, queryset):
        '''显示评论'''
        queryset.update(is_hide=False)
    enable_commentstatus.short_description = '显示评论'

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


@admin.register(MpComments)
class MpCommentAdmin(DraggableMPTTAdmin):
    mptt_indent_field = "body"

    # 搜索字段
    search_fields = ['body']
    # 过滤器
    list_filter = ['is_overhead', 'is_hide', 'object_id', 'content_type', 'parent_comment']  
    actions = ['enable_commentstatus', 'disable_commentstatus', 'enable_overhead', 'disable_overhead']
    # 可点击的项
    list_display_links = ('indented_title',)

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

