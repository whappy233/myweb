from myweb.utils import cache
from .models import AboutBlog
from django.shortcuts import render



# 关于
def AboutView(request):
    obj = AboutBlog.objects.first()
    if obj:
        ud = obj.update_date.strftime("%Y%m%d%H%M%S")
        md_key = '{}_md_{}'.format(obj.id, ud)
        cache_md = cache.get(md_key)
        if cache_md:
            body = cache_md
        else:
            body = obj.body_to_markdown()
            cache.set(md_key, body, 3600 * 24 * 15)
    else:
        repo_url = 'https://github.com/Hopetree'
        body = '<li>作者 Github 地址：<a href="{}">{}</a></li>'.format(repo_url, repo_url)
    return render(request, 'blog/about.html', context={'body': body})

