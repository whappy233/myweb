import base64
import io
from os import readlink

from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.db import connections
from django.http.response import (HttpResponse, HttpResponseForbidden,
                                  JsonResponse)
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from PIL import Image

from app_common.utils import JSONEncoder
from .models import Gallery, Photo


# 相册列表
# 使用基于类的视图时，需要按如下方法使用method_decorator的这个装饰器。其作用是把类伪装成函数，然后再应用login_required这个装饰器
# 或者在url中使用 path('', login_required(views.GalleryListView.as_view()), name='gallery_list')
@method_decorator(login_required, name='dispatch')
class GalleryListView(ListView):
    queryset = Gallery.nonEmpty.filter(is_visible=True)
    paginate_by = 20
    template_name = 'tp/gallery_index.html'  # 使用自定义模板渲染

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'gallery'
        return context


# 相册详细  only allow Ajax (GET)
@method_decorator(login_required, name='dispatch') # dispatch 表示所有请求，因为所有请求都先经过dispatch
class GalleryDetail(ListView):

    model = Photo
    paginate_by = 10

    def get_queryset(self):
        queryset = super(GalleryDetail, self).get_queryset()
        gallery_pk = self.request.GET.get('pk')
        gallery_uuid = self.request.GET.get('uuid')
        queryset = queryset.filter(gallery__pk=gallery_pk, gallery__uuid=gallery_uuid)
        return queryset

    def get(self, request, *args, **kwargs):
        if not self.request.is_ajax():
            return HttpResponseForbidden()

        self.object_list = self.get_queryset()
        context = self.get_context_data()
        paginator = context.get('paginator')
        page_obj = context.get('page_obj')

        zz = serializers.serialize("json", self.object_list, 
                fields=('alt', 'thumb', 'image', 'create_date'), 
                ensure_ascii=False)

        data = {
            'current_page': page_obj.number,    # 当前页码
            "page_total": paginator.num_pages,  # 总页数
            "items_count": paginator.count,     # 元素总数
            "items": zz
        }

        return JsonResponse(data, encoder=JSONEncoder)



def random_photo(request, width, height):
    photo = Photo.objects.get_random_photo()
    photo = Image.open(photo.image.path)

    x = int(width)
    y = int(height)
    size = (x ,y)

    crop_im = photo.resize(size, Image.ANTIALIAS)
    img_buffer = io.BytesIO()
    crop_im.save(img_buffer, format='png')
    byte_data = img_buffer.getvalue()
    return HttpResponse(byte_data)



# 剪裁随机图片
def get_random_background(request, x, y):  # 定义标签
    photo = Photo.objects.first()
    if photo:
        photo = Image.open(photo.image.path)
        size_ = photo.size

        x = int(x)
        y = int(y)
        if x and y:
            size = (x ,y)
        else: size = size_

        crop_im = photo.resize(size, Image.ANTIALIAS)
        img_buffer = io.BytesIO()
        crop_im.save(img_buffer, format='png')
        byte_data = img_buffer.getvalue()
        return HttpResponse(byte_data)
    return HttpResponse('')

