from django.contrib.auth import models
import xadmin
from django.contrib.auth.models import User
from app_user.models import UserProfile
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.safestring import mark_safe




class UserProfileAdmin:
    list_display = ['user', 'photo', 'introduction', 'telephone', 'mod_date']  # 要显示的字段
    search_fields = ['user', 'telephone']   # 搜索字段
    list_filter = ['user']                  # 过滤器
    readonly_fields = ('user',)             # 只读字段

    # def get_readonly_fields(self, **kwargs):
    #     """ 重新定义此函数，限制普通用户所能修改的字段  """
    #     print(10*'-')
    #     print(self.org_obj)
    #     if self.user.is_superuser:
    #         self.readonly_fields = []
    #     return self.readonly_fields


xadmin.site.register(UserProfile, UserProfileAdmin)
