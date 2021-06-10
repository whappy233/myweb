import datetime
import decimal

from django.contrib.humanize.templatetags import humanize
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.base import ModelBase
from django.utils.encoding import smart_text
from loguru import logger
from django.core.cache import cache


def get_blog_setting():
    value = cache.get('get_blog_setting')
    if value:
        return value
    else:
        from .models import BlogSettings
        if not BlogSettings.objects.count():
            setting = BlogSettings()
            setting.sitename = '星海StarSea'
            setting.site_description = '该说些什么好呢?啊哈哈哈'
            setting.site_seo_description = '基于Django的博客系统'
            setting.site_keywords = 'Django,Python'
            setting.article_sub_length = 10   # 文章摘要长度
            setting.sidebar_article_count = 10
            setting.sidebar_comment_count = 5
            setting.show_google_adsense = False
            setting.allow_register = False  # 允许注册?
            setting.open_site_comment = True  # 全站评论
            setting.analyticscode = ''   # 分析代码
            setting.beiancode = ''  # 备案号
            setting.show_gongan_code = False
            setting.save()
        value = BlogSettings.objects.first()
        logger.info('set cache get_blog_setting')
        cache.set('get_blog_setting', value)
        return value


class JSONEncoder(DjangoJSONEncoder):

    def default(self, o):
        if isinstance(o, datetime.datetime):
            return humanize.naturaltime(o)
            # return o.strftime('%Y年%m月%d日 %H:%M:%S')
        elif isinstance(o, datetime.date):
            return o.strftime('%Y-%m-%d')
        elif isinstance(o, decimal.Decimal):
            return str(o)
        elif isinstance(o, ModelBase):
            return '%s.%s' % (o._meta.app_label, o._meta.model_name)
        else:
            try:
                return super(JSONEncoder, self).default(o)
            except Exception:
                return smart_text(o)







