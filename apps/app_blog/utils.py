import mistune
from mistune import escape, escape_link
from pygments import highlight
from pygments.formatters import html
from pygments.lexers import get_lexer_by_name
from myweb.utils import get_current_site, cache
from loguru import logger


# markdown -------------------------------------------------------------
def block_code(text, lang, inlinestyles=False, linenos=False):
    '''markdown代码高亮'''
    if not lang:
        text = text.strip()
        return u'<pre><code>%s</code></pre>\n' % mistune.escape(text)
    try:
        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = html.HtmlFormatter(noclasses=inlinestyles, linenos=linenos)
        code = highlight(text, lexer, formatter)
        if linenos:
            return f'<div class="highlight">{code}</div>\n'
        return code
    except BaseException:
        return f'<pre class="{lang}"><code>{mistune.escape(text)}</code></pre>\n'

class BlogMarkDownRenderer(mistune.Renderer):
    '''markdown渲染'''

    def block_code(self, text, lang=None):
        # renderer has an options
        inlinestyles = self.options.get('inlinestyles')
        linenos = self.options.get('linenos')
        return block_code(text, lang, inlinestyles, linenos)

    def autolink(self, link, is_email=False):
        text = link = escape(link)

        if is_email:
            link = f'mailto:{link}'
        if not link:
            link = "#"
        site = get_current_site()
        nofollow = "" if link.find(site.domain) > 0 else "rel='nofollow'"
        return f'<a href="{link}" {nofollow}>{text}</a>'

    def link(self, link, title, text):
        link = escape_link(link)
        site = get_current_site()
        nofollow = "" if link.find(site.domain) > 0 else "rel='nofollow'"
        if not link:
            link = "#"
        if not title:
            return f'<a href="{link}" {nofollow}>{text}</a>'
        title = escape(title, quote=True)
        return f'<a href="{link}" title="{title}" {nofollow}>{text}</a>'

class CommonMarkdown():
    @staticmethod
    def get_markdown(value):
        renderer = BlogMarkDownRenderer(inlinestyles=False)

        mdp = mistune.Markdown(escape=True, renderer=renderer)
        return mdp(value)



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