
import markdown
from django import template
from django.db.models import Count
from django.utils.safestring import mark_safe  # 标记为安全的html

from ..models import Post

register = template.Library()

# 自定义模板标签 过滤器
# 值使用自定义模板标签 和过滤器时 应该在模板中首先在开头引入 {% load xxxx %}


# 自定义模板标签1
# 文章总数
# simple_tag (处理数据并返回一个字符串)  {% total_posts %}
@register.simple_tag(name='total_posts')  # 注册模板标签和过滤器, 默认使用函数名作为标签名字，也可自定义 @register.simple_tag(name='name')
def total_posts():  # 定义标签
    return Post.published.count()

# 最多评论
@register.simple_tag
def get_most_commented_posts(count=5):
    return Post.published.annotate(total_comments=Count('comments')).order_by('-total_comments')[:count]

# 自定义模板标签2
# 最近更新
# inclusion_tag (处理数据并返回模板)   {% show_latest_posts 5 %}
@register.inclusion_tag('app_blog/latest_posts.html')  # 指定利用返回值显示的模板
def show_latest_posts(count=5):
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts':latest_posts}

# ------------------------------------------------------------------------------------
# 自定义模板过滤器
# 过滤器 (转换为makedown)  {{ post.body| markdown }}
@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))
