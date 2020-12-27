# 帖子订阅 (?)

from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords  # 过滤器
from .models import Post


class LatestPostsFeed(Feed):
    title = 'My blog'  # <title>
    link = '/blog/'  # <link>
    description = 'New posts of my blog'  # <description>

    def items(self):
        return Post.published.all()[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return truncatewords(item.body, 30)  # 过滤器 (前30个词)
