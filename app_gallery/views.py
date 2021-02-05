from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Gallery, Photo

# 相册列表
# 使用基于类的视图时，需要按如下方法使用method_decorator的这个装饰器。其作用是把类伪装成函数，然后再应用login_required这个装饰器
# 或者在url中使用 path('', login_required(views.GalleryListView.as_view()), name='gallery_list')
@method_decorator(login_required, name='dispatch')
class GalleryListView(ListView):
    queryset = Gallery.objects.filter(is_visible=True)
    paginate_by = 10
    template_name = 'app_gallery/gallery_list.html'  # 使用自定义模板渲染
    # template_name = 'app_gallery/index.html'  # 使用自定义模板渲染

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




import base64
import io
from PIL import Image


def crop_image(file, size=None, box=None, r=0):
    '''
    box: (x轴剪裁起点, Y轴剪裁起点, w剪裁后的宽度, h剪裁后高度)
    size: 剪裁后的宽高
    r: 旋转角度
    '''
    photo = Image.open(file)
    size_ = photo.size
    if not size:
        size = size_
    if isinstance(size, (int, float)):
        size = int(size_[0]/size), int(size_[1]/size)
    if not box:
        box = (0, 0, *size_)
    # crop: 返回此图像的矩形区域。 该框是一个四元组，定义了左，上，右和下像素坐标
    # resize: 返回此图像的调整大小的副本。
    # roator: 返回此图像的旋转副本。 此方法返回此图像的副本，并围绕其中心逆时针旋转给定的度数
    crop_im = photo.crop(box).resize(size, Image.ANTIALIAS).rotate(r)
    return crop_im

def pil_base64(image):
    img_buffer = io.BytesIO()
    image.save(img_buffer, format='png')
    byte_data = img_buffer.getvalue()
    base64_str = base64.b64encode(byte_data).decode()
    return base64_str


def get_random_background(request, size=None, box=None, r=0):  # 定义标签
    photo = Photo.objects.get_random_photo()
    image = crop_image(photo.image.path, size, box, r)
    return pil_base64(image)



