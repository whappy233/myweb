from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile


# User 和 UserProfile 是一对一关系, 
# UserProfile 的目的是增加额外的用户字段, 
# 要在 Admin 界面修改 User 表时同时可以编辑 UserProfile.
# 方式如下:

class UserProfileInline(admin.StackedInline):
    model = UserProfile

class UserProfileAdmin(UserAdmin):
    inlines = [UserProfileInline, ]

admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)