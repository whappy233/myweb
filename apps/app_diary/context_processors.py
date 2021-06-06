
from django.urls import reverse
from .models import Diary


def contexts(request):
    ''' 获取 Admin 的新建文章 URL '''
    info = (Diary._meta.app_label, Diary._meta.model_name)
    # return {'add_article': reverse('admin:%s_%s_add' % info)}  # admin
    return {
        'diary_xadmin': reverse('xadmin:%s_%s_changelist' % info),
        'diary_xadmin_add': reverse('xadmin:%s_%s_add' % info),
        }   # xadmin

