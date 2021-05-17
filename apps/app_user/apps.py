from django.apps import AppConfig


class AppUserConfig(AppConfig):
    name = 'app_user'
    verbose_name = '用户'

    # 设置app图标
    app_icon = 'fa-fw fa fa-user'


    def ready(self):  # 执行初始化任务,例如注册信号和连接non-SQL数据库
        from . import signals
        return super().ready()