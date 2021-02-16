'xadmin 全局配置'

import xadmin
from app_user.models import UserProfile
from django.contrib.auth.models import Group, Permission

class BaseSetting:
    """xadmin的基本配置"""
    enable_themes = True      # 开启主题切换功能
    use_bootswatch = True     # 支持切换主题

xadmin.site.register(xadmin.views.BaseAdminView, BaseSetting)



class GlobalSettings:
    """xadmin的全局配置"""

    site_title = "我的后台"         # 设置站点标题
    site_footer = "Carlos"        # 设置站点的页脚
    # menu_style = "accordion"    # 设置菜单折叠，在左侧，默认的
    # 设置models的全局图标, UserProfile, Sports 为表名
    global_search_models = [UserProfile]
    global_models_icon = {UserProfile: "glyphicon glyphicon-user"}

    def go_to(self):  # 设置列表页跳转
        from django.utils.safestring import mark_safe
        return mark_safe('<a href="http://www.fishc.com.cn">跳转</a>')
    go_to.short_description = '链接ghbdfghghhfgjfgjfhjfghjfgjfghjfgjfghjfgj'

    # def get_site_menu(self):
    #     '''自定义导航菜单顺序'''
    #     return (
    #         {'title': '用户管理', 'menus': (
    #             {'title': '用户信息', 'url': self.get_model_url(UserProfile, 'changelist')},
    #             # {'title': '用户验证', 'url': self.get_model_url(EmailVerifyRecord, 'changelist')},
    #             # {'title': '用户课程', 'url': self.get_model_url(UserCourse, 'changelist')},
    #             # {'title': '用户收藏', 'url': self.get_model_url(UserFavorite, 'changelist')},
    #             # {'title': '用户消息', 'url': self.get_model_url(UserMessage, 'changelist')},
    #         )},
    #         {'title': '系统管理', 'menus': (
    #             {'title': '用户分组', 'url': self.get_model_url(Group, 'changelist')},
    #             {'title': '用户权限', 'url': self.get_model_url(Permission, 'changelist')},
    #         )},
    #     )


xadmin.site.register(xadmin.views.CommAdminView, GlobalSettings)