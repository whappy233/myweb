'xadmin 全局配置'

from typing import Callable
import xadmin
from django.contrib.auth.models import Group, Permission
from .models import BlogSettings, Carousel
from django.utils.safestring import mark_safe

from app_user.models import UserProfile
from app_blog.models import Article, Category
from app_gallery.models import Gallery, Photo
from app_comments.models import Comments



class BaseSetting:
    """xadmin的基本配置"""
    enable_themes = True      # 开启主题切换功能
    use_bootswatch = True     # 支持切换主题

xadmin.site.register(xadmin.views.BaseAdminView, BaseSetting)



class GlobalSettings:
    """xadmin的全局配置"""

    site_title = "浩瀚星海"         # 设置站点标题
    site_footer = "浩瀚星海 2021"   # 设置站点的页脚
    # menu_style = "accordion"     # 设置菜单折叠，在左侧，默认的

    global_search_models = [UserProfile]

    # 设置models的全局图标
    global_models_icon = {
        UserProfile: "glyphicon glyphicon-user",
        Article: "glyphicon glyphicon-leaf",
        Category: "glyphicon glyphicon-th-list",
        Gallery: "glyphicon glyphicon-book",
        Photo: "glyphicon glyphicon-picture",
        Comments: "glyphicon glyphicon-comment",
        BlogSettings: "glyphicon glyphicon-cog",
        Carousel: "glyphicon glyphicon-sound-stereo",
    }

    def go_to(self):  # 设置列表页跳转
        return mark_safe('<a href="http://www.fishc.com.cn">跳转</a>')
    go_to.short_description = '链接hjfgj'

    def get_site_menu(self):
        '''自定义导航菜单顺序'''
        return (
            {'title': '用户管理', 'menus': (
                {'title': '用户信息', 'url': self.get_model_url(UserProfile, 'changelist')},
                # {'title': '用户验证', 'url': self.get_model_url(EmailVerifyRecord, 'changelist')},
                # {'title': '用户课程', 'url': self.get_model_url(UserCourse, 'changelist')},
                # {'title': '用户收藏', 'url': self.get_model_url(UserFavorite, 'changelist')},
                # {'title': '用户消息', 'url': self.get_model_url(UserMessage, 'changelist')},
            )},
            {'title': '系统管理', 'menus': (
                {'title': '用户分组', 'url': self.get_model_url(Group, 'changelist')},
                {'title': '用户权限', 'url': self.get_model_url(Permission, 'changelist')},
            )},
        )

xadmin.site.register(xadmin.views.CommAdminView, GlobalSettings)




# 轮播图
class CarouselAdmin:
    list_display = ['id', 'number', 'title', 'content', 'img_url', 'url']
    search_fields = ['title',]
    ordering = ['number', '-id'] 
xadmin.site.register(Carousel, CarouselAdmin)


# 网站配置
class BlogSettingsAdmin:
    pass
xadmin.site.register(BlogSettings, BlogSettingsAdmin)
