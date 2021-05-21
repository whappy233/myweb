from django.apps import AppConfig


class AppCommentsConfig(AppConfig):
    name = 'app_comments'
    verbose_name = '评论'

    def ready(self) -> None:
        from . import signals
        return super().ready()
