from django.apps import AppConfig


class AppUserConfig(AppConfig):
    name = 'app_user'
    verbose_name = '用户'

    # def ready(self):  # 执行初始化任务,例如注册信号和连接non-SQL数据库
    #     ...