
import markdown
from django import template
from django.db.models import Count
from django.utils.safestring import mark_safe  # 标记为安全的html

from ..models import Article

register = template.Library()

# 自定义模板标签 过滤器
# 在使用自定义模板标签 和过滤器时 应该在模板中首先在开头引入 {% load xxxx %}


# 自定义模板标签 ------------------------------------------------------------------------------------
# 文章总数
# simple_tag (处理数据并返回一个字符串或者给context设置或添加变量)  {% total_articles %}
@register.simple_tag(name='total_articles')  # 注册模板标签和过滤器, 默认使用函数名作为标签名字，也可自定义 @register.simple_tag(name='name')
def total_articles():  # 定义标签
    return Article.published.count()

# 最多评论
@register.simple_tag
def get_most_commented_articles(count=5):
    return Article.published.annotate(total_comments=Count('comments')).order_by('-total_comments')[:count]

# 最近更新
# inclusion_tag (处理数据并返回模板)   {% show_latest_articles 5 %}
@register.inclusion_tag('app_blog/latest_articles.html')  # 指定利用返回值显示的模板
def show_latest_articles(count=5):
    latest_articles = Article.published.order_by('-publish')[:count]
    return {'latest_articles':latest_articles}

# 在设置 takes_context=True 后, 可以直接使用 context 里的变量.
# {% show_results %} 不再需要 poll 这个参数，即可显示 poll 的结果
'''
@register.inclusion_tag('results.html', takes_context=True)
def show_results(context):
    choices = context['poll'].choice_set.all()
    return {'choices': choices}
'''

# 处理从模板中传递过来的多个参数
# 如果参数名字或数量已知，Django的tag函数是可以按位置处理传递过来的参数
# {% my_tag "abcd" book.title warning=message profile=user.profile %}
'''
@register.inclusion_tag('my_template.html')
def my_tag(a, b, *args, **kwargs):
    warning = kwargs['warning']
    profile = kwargs['profile']
    ...
    return ...
'''

# <p>Published at at {% format_time article.pub_date "%Y-%m-%d %I:%M %p" %}.</p>
@register.tag(name="format_time")
def do_format_time(parser, token):
    # 获取 format_time article.pub_date "%Y-%m-%d %I:%M %p" 这一长串字符串作为token
    try:
        # split_contents（）知道不拆分带引号的字符串
        tag_name, date_to_be_formatted, format_string = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires exactly two arguments" % token.contents.split()[0]
        )
    if not (format_string[0] == format_string[-1] and format_string[0] in ('"', "'")):
        raise template.TemplateSyntaxError(
            "%r tag's argument should be in quotes" % tag_name
        )
    return FormatTimeNode(date_to_be_formatted, format_string[1:-1])

class FormatTimeNode(template.Node):
    def __init__(self, date_to_be_formatted, format_string):
        self.date_to_be_formatted = template.Variable(date_to_be_formatted)
        self.format_string = format_string
 
    def render(self, context):
        try:
            actual_date = self.date_to_be_formatted.resolve(context)
            return actual_date.strftime(self.format_string)  # 2020-12-30 04:28 PM  (str)
            # 可以通过 context 给模板传递其它的变量（如下所示)。当render方法不返回一个具体的值的时候，需要返回一个空字符串
            # context['formatted_time'] = actual_date.strftime(self.format_string)  #  {{ formatted_time }}
            # return ''
        except template.VariableDoesNotExist:
            return ''








# 自定义模板过滤器 ------------------------------------------------------------------------------------
# { 使用 '|' 前的值}
# 过滤器 (转换为makedown)  {{ article.body| markdown }}
@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))

import datetime
@register.filter(name='chinese_date_format')
def chinese_date_format(value):
    if isinstance(value, datetime.datetime):
        return "{}年{}月{}日".format(value.year, value.month, value.day)
    else:
        return value

# {{ value | add_description:args }}
# {{ article.title | add_description:"最热" }}时，标题后面会加上"最热"字样
@register.filter(name='add_description')
def add_description(value, args):
    return "{} ({})".format(value, args)