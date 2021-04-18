from myweb.utils import  cache
from loguru import logger


def get_blog_setting():
    value = cache.get('get_blog_setting')
    if value:
        return value
    else:
        from .models import BlogSettings
        if not BlogSettings.objects.count():
            setting = BlogSettings()
            setting.sitename = 'DjangoBlog'
            setting.site_description = '基于Django的博客系统'
            setting.site_seo_description = '基于Django的博客系统'
            setting.site_keywords = 'Django,Python'
            setting.article_sub_length = 10   # 文章摘要长度
            setting.sidebar_article_count = 10
            setting.sidebar_comment_count = 5
            setting.show_google_adsense = False
            setting.open_site_comment = True
            setting.analyticscode = ''
            setting.beiancode = ''
            setting.show_gongan_code = False
            setting.save()
        value = BlogSettings.objects.first()
        logger.info('set cache get_blog_setting')
        cache.set('get_blog_setting', value)
        return value