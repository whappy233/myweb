'xadmin 全局配置'

import xadmin
from xadmin.sites import register
from django.contrib.auth.models import Group, Permission
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User
from .models import BlogSettings, Carousel
from app_user.models import UserProfile
from app_blog.models import Article, Category
from app_gallery.models import Gallery, Photo
from app_comments.models import Comments, MpComments
from app_blog.cn_taggit import CnTag


@register(xadmin.views.base.BaseAdminView)
class BaseSetting:
    """xadmin的基本配置"""
    enable_themes = True      # 开启主题切换功能
    use_bootswatch = True     # 支持切换主题


@register(xadmin.views.CommAdminView)
class GlobalSettings:
    """xadmin的全局配置"""

    site_title = "浩瀚星海"         # 设置站点标题
    site_footer = "浩瀚星海 2021"   # 设置站点的页脚
    # menu_style = "accordion"     # 设置菜单折叠，在左侧，默认的
    list_display = ['go_to']

    global_search_models = [UserProfile]

    def get_site_menu(self):
        '''自定义导航菜单顺序'''
        url = reverse('admin:%s_%s_changelist' % (MpComments._meta.app_label, MpComments._meta.model_name))
        return (
            {'title': '用户管理', 'menus': (
                {'title': 'User', 'url': self.get_model_url(User, 'changelist'), 'icon': 'glyphicon glyphicon-user'},
                {'title': 'Profile', 'url': self.get_model_url(UserProfile, 'changelist'), 'icon': 'glyphicon glyphicon-user'},
            )},
            {'title': '博客管理', 'menus': (
                {'title': '文章', 'url': self.get_model_url(Article, 'changelist') ,'icon': "glyphicon glyphicon-leaf"},
                {'title': '分类', 'url': self.get_model_url(Category, 'changelist') ,'icon': "glyphicon glyphicon-th-list"},
                {'title': '标签', 'url': self.get_model_url(CnTag, 'changelist') ,'icon': "glyphicon glyphicon-tag"},
            )},
            {'title': '相册', 'menus': (
                {'title': '相册', 'url': self.get_model_url(Gallery, 'changelist') ,'icon': "glyphicon glyphicon-book"},
                {'title': '相片', 'url': self.get_model_url(Photo, 'changelist') ,'icon': "glyphicon glyphicon-picture"},
            )},
            {'title': '评论系统', 'menus': (
                {'title': '评论', 'url': self.get_model_url(Comments, 'changelist') ,'icon': "glyphicon glyphicon-comment"},
                {'title': 'MP Comments', 'url': self.get_model_url(MpComments, 'changelist') ,'icon': "glyphicon glyphicon-tree-conifer"},
                {'title': 'MP Admin', 'url': url, 'icon': 'glyphicon glyphicon-move'},
            )},
            {'title': '通用', 'menus': (
                {'title': '轮播图', 'url': self.get_model_url(Carousel, 'changelist'),'icon': "glyphicon glyphicon-sound-stereo"},
                {'title': '站点配置', 'url': self.get_model_url(BlogSettings, 'changelist') ,'icon': "glyphicon glyphicon-cog"},
            )},
        )


# 轮播图
@register(Carousel)
class CarouselAdmin:
    list_display = ['id', 'number', 'title', 'content', 'img_url', 'url']
    search_fields = ['title',]
    ordering = ['number', '-id'] 


# 网站配置
@register(BlogSettings)
class BlogSettingsAdmin:
    pass
