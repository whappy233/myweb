import markdown
from bs4 import BeautifulSoup
from django.utils.text import slugify

EXTENSIONS = (
    'extra',  # 'markdown.extensions.extra',
    'codehilite',
    'toc',
    # 'tables',
    # 'fenced_code',
    # CodeHiliteExtension(linenums=False),
    # TocExtension(slugify=slugify),
)

CONFIG = {
    'codehilite': {
        'linenums': True
    },
    'toc': {
        'slugify': slugify
    }
}


def MarkdownRender(content):

    md = markdown.Markdown(extensions=EXTENSIONS, extension_configs=CONFIG)

    body = md.convert(content)
    # 把换行符替换成两个空格+换行符，这样经过markdown转换后才可以转成前端的br标签
    # body = md.convert(content.replace("\r\n", '  \n'))
    toc = md.toc  # 目录
    soup = BeautifulSoup(body, "html.parser")
    _add_img_attrs(soup)
    return soup.prettify(), toc


def _add_img_attrs(soup):
    '''给图像添加延迟加载属性及样式'''

    # <img class="loading" data-src="https://picsum.photos/id/10{{forloop.counter}}/380/240">
    for tag in soup.find_all("img"):
        if tag.has_attr('class'):
            tag['class'] += " loading"
        else:
            tag['class'] = "loading"
        
        if tag.has_attr('src'):
            tag['data-src'] = tag['src']
            del tag['src']