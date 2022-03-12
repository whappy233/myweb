from django.apps import AppConfig


class AppBlogConfig(AppConfig):
    name = 'app_blog'
    verbose_name = '博客'

    def ready(self) -> None:
        '''在 django 启动前做一些事情'''

        # from django.utils.module_loading import autodiscover_modules
        # autodiscover_modules("aaaa")
        return super().ready()
