from bs4 import BeautifulSoup
import markdown
from markdown.extensions.toc import TocExtension  # 锚点的拓展
from django.utils.text import slugify


def MarkdownRender(content):

    md = markdown.Markdown(extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        TocExtension(slugify=slugify),
    ])

    body = md.convert(content)
    # 把换行符替换成两个空格+换行符，这样经过markdown转换后才可以转成前端的br标签
    # body = md.convert(content.replace("\r\n", '  \n'))
    toc = md.toc  # 目录
    soup = BeautifulSoup(body, "html.parser")
    _add_img_attrs(soup)
    return soup.prettify(), toc


def _add_img_attrs(soup):
    # <img class="loading" data-src="https://picsum.photos/id/10{{forloop.counter}}/380/240">
    for tag in soup.find_all("img"):
        if tag.has_attr('class'):
            tag['class'] += " loading"
        else:
            tag['class'] = "loading"
        
        if tag.has_attr('src'):
            tag['data-src'] = tag['src']
            del tag['src']