import base64
import io
from ..models import Photo
from django import template
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



# <img src="data:image/png;base64,{% get_random_background 4 %}" alt="" class="img-responsive">

register = template.Library()
'simple_tag (处理数据并返回一个字符串或者给context设置或添加变量)  {% get_random_background 0.5 %}'
@register.simple_tag  # 注册模板标签和过滤器, 默认使用函数名作为标签名字，也可自定义 @register.simple_tag(name='name')
def get_random_background(size=None, box=None, r=0):  # 定义标签
    photo = Photo.objects.get_random_photo()
    if photo:
        image = crop_image(photo.image.path, size, box, r)
        return pil_base64(image)
    else:
        return ''

def pil_base64(image):
    img_buffer = io.BytesIO()
    image.save(img_buffer, format='png')
    byte_data = img_buffer.getvalue()
    base64_str = base64.b64encode(byte_data).decode()
    return base64_str

