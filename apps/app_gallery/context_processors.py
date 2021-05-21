from .models import Gallery, Photo
from django.urls import reverse


def contexts(request):
    ''' 获取 Admin 的新增相册(Gallery) URL '''
    info1 = (Photo._meta.app_label, Photo._meta.model_name)
    info2 = (Gallery._meta.app_label, Gallery._meta.model_name)
    return {
        'add_photo': reverse('xadmin:%s_%s_add' % info1),  # xadmin
        'add_gallery': reverse('xadmin:%s_%s_add' % info2),

        # 'add_photo': reverse('admin:%s_%s_add' % info1),  # admin
        # 'add_gallery': reverse('admin:%s_%s_add' % info2),
        }