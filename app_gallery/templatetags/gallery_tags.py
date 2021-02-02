from django import template
from app_gallery.models import Photo


register = template.Library()


'simple_tag (处理数据并返回一个字符串或者给context设置或添加变量)  {% get_random_background %}'
@register.simple_tag  # 注册模板标签和过滤器, 默认使用函数名作为标签名字，也可自定义 @register.simple_tag(name='name')
def get_random_background():  # 定义标签
    photo = Photo.objects.get_random_photo()
    return photo.image.url