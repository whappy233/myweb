
from .models import Article
from django.urls import reverse


def contexts(request):
    ''' 获取 Admin 的新建文章 URL '''
    info = (Article._meta.app_label, Article._meta.model_name)
    # return {'add_article': reverse('admin:%s_%s_add' % info)}  # admin
    return {'add_article': reverse('xadmin:%s_%s_add' % info)}   # xadmin

