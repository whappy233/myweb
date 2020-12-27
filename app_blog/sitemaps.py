# 网站地图 (http://127.0.0.1:8000/sitemap.xml)

from django.contrib.sitemaps import Sitemap
from .models import Post


class PostSitemap(Sitemap):
    # 'always' 'hourly' 'daily'
    # 'weekly' 'monthly' 'yearly' 'never'
    changefreq = 'weekly' # 更新频率
    priority = 0.9  # 优先级, 最大为 1
    # protocol = 'http'  # 定义URL的协议（'http'或'https'）。如果未设置，则使用请求站点地图的协议。如果站点地图是在请求上下文之外构建的，则默认值为'http'

    def items(self):
        '''只是返回序列 或QuerySet对象
        返回的结果会传递给对应站点地图属性的任何可调用的方法(location, lastmod, changefreq 和 priority)'''
        return Post.published.all()  # 默认状态下对每个对象调用 get_absolute_url() 方法并检索其URL

    # 检索 items() 返回的各个对象 返回对象最近修时间
    def lastmod(self, obj):
        '''返回一个datetime'''
        return obj.updated