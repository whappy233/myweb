import io
from os import readlink
from django.contrib.auth.decorators import login_required
from django.db import connections
from django.http.response import Http404, HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView
from PIL import Image
from django.shortcuts import render
from .models import Gallery, Photo
import json

from django.core import serializers




# 相册列表
# 使用基于类的视图时，需要按如下方法使用method_decorator的这个装饰器。其作用是把类伪装成函数，然后再应用login_required这个装饰器
# 或者在url中使用 path('', login_required(views.GalleryListView.as_view()), name='gallery_list')
@method_decorator(login_required, name='dispatch')
class GalleryListView(ListView):
    queryset = Gallery.notNull.filter(is_visible=True)
    paginate_by = 20
    template_name = 'tp/gallery_index.html'  # 使用自定义模板渲染

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'gallery'
        return context


# 相册详细
# 使用基于类的视图时，需要按如下方法使用method_decorator的这个装饰器。其作用是把类伪装成函数，然后再应用login_required这个装饰器
# 或者在url中使用 re_path('xxx', login_required(views.GalleryDetail.as_view()), name='gallery_detail'),
@method_decorator(login_required, name='dispatch')  # dispatch 表示所有请求，因为所有请求都先经过dispatch
class GalleryDetail(DetailView):
    model = Gallery
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images'] = Photo.objects.filter(gallery=self.object.id) # 相册下的所有文件
        context['section'] = 'gallery'
        return context


@method_decorator(login_required, name='dispatch')
class ZXX(ListView):

    model = Photo
    paginate_by = 10

    def get_queryset(self):
        queryset = super(ZXX, self).get_queryset()
        gallery_pk = self.request.GET.get('pk')
        gallery_slug = self.request.GET.get('slug')
        queryset = queryset.filter(gallery__pk=gallery_pk, gallery__slug=gallery_slug)
        return queryset

    def get(self, request, *args, **kwargs):
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
            "items": json.loads(zz)
        }

        print(data)

        return JsonResponse(data)



# 剪裁随机图片
def get_random_background(request, x, y):  # 定义标签
    photo = Photo.objects.get_random_photo()
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

