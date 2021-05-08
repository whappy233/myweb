import io

from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView
from PIL import Image

from .models import Gallery, Photo


# 相册列表
# 使用基于类的视图时，需要按如下方法使用method_decorator的这个装饰器。其作用是把类伪装成函数，然后再应用login_required这个装饰器
# 或者在url中使用 path('', login_required(views.GalleryListView.as_view()), name='gallery_list')
@method_decorator(login_required, name='dispatch')
class GalleryListView(ListView):
    queryset = Gallery.objects.filter(is_visible=True)
    paginate_by = 10
    template_name = 'app_gallery/gallery_list.html'  # 使用自定义模板渲染

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
    template_name = 'app_gallery/gallery_detail.html'  # 使用自定义模板渲染
    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['images'] = Photo.objects.filter(gallery=self.object.id) # 相册下的所有文件
        context['section'] = 'gallery'
        return context


# 剪裁随机图片
def get_random_background(request, x, y):  # 定义标签
    photo = Photo.objects.get_random_photo()
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



