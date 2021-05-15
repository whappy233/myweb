from xadmin.plugins.auth import UserAdmin
from django.contrib.auth import models
from django.contrib.auth.models import User
from .models import UserProfile
from django.utils.html import format_html
from django.utils.safestring import mark_safe

import xadmin
from xadmin.sites import register

@register(UserProfile)
class UserProfileAdmin:
    list_display = ['user', 'show_img', 'introduction', 'telephone', 'mod_date']  # 要显示的字段
    search_fields = ['user__username', 'user__email', 'telephone']   # 搜索字段
    list_filter = ['user__is_staff', 'user__is_active', 'user__is_superuser', 'user__date_joined']  # 过滤器
    readonly_fields = ('user',)             # 只读字段

    def show_img(self, obj):
        '''展示封面'''
        url = obj.photo.url
        return format_html(f'<img style="width:22px;height:22px" src="{url}"></img>')
    show_img.short_description = '头像'  # 设置表头


    # def get_readonly_fields(self, **kwargs):
    #     """ 重新定义此函数，限制普通用户所能修改的字段  """
    #     print(10*'-')
    #     print(self.org_obj)
    #     if self.user.is_superuser:
    #         self.readonly_fields = []
    #     return self.readonly_fields



class UserProfileInline:
    model = UserProfile
    extra = 0
    style= 'one'  # 列表显示，one：只显示一条  accordion：缩略列表显示，可下拉  tab：横向tab显示 stacked：块显示 table：列表


class UserAdmin(UserAdmin):
    # 用户创建的项目
    inlines = [UserProfileInline]

xadmin.site.unregister(User)
xadmin.site.register(User, UserAdmin)

