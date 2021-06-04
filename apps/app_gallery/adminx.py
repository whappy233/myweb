

import os
import uuid
import zipfile
from django.core.files.base import ContentFile
import loguru
from .models import Gallery, Photo
from .forms import GalleryForm
from django.utils.html import format_html
from loguru import logger
from xadmin.sites import register


lightense = '''
<script src="/static/st/js/lightense.min.js"></script>
<script>
window.addEventListener('load', function () {
    var el = document.querySelectorAll('td>img.field_img');
    Lightense(el, {
        time: 300,
        padding: 40,
        offset: 40,
        keyboard: true,
        cubicBezier: 'cubic-bezier(.2, 0, .1, 1)',
        background: 'rgba(0, 0, 0, .8)',
        zIndex: 2147483647
    })
}, false);
</script>'''


@register(Gallery)
class GalleryModelAdmin:
    form = GalleryForm
    list_display = ('id', 'title', 'uuid', 'created_time', 'last_mod_time', 'is_delete', 'is_visible', 'show_thumb_img')
    list_filter = ('created_time',)
    ordering = ['-last_mod_time']
    list_editable = ['title', 'thumb', 'is_delete', 'is_visible']
    list_display_links = ['uuid']

    # 为什么要重写save_model方法?
    # 当我们通过 GalleryForm 创建 gallery 对象时，默认的form.save()方法只能将相关字段存入到 Gallery 模型对应的表单里。
    # 那我们上传的zip文件包里的图片怎么办？我们怎样把它解压后也存入 Pthoto 模型对应的表单里？
    # 我们希望在存储图片前对其重命名怎么办？默认的方式的按原文件名进行存储。
    # Photo 的thumb字段默认为空，我们怎么将用户上传的图片进行压缩处理后存入这个字段使其不为空？

    # save_model方法，对文件包解压，图片的重命名及存储
    # Django自带的save_model方法为admin界面用户保存model实例时的行为
    # request为HttpRequest实例
    # obj为model实例
    # form为ModelForm实例
    # change为bool值，取决于model实例是新增的还是修改的
    def save_models(self):
        # request = self.request
        # obj  = self.new_obj
        # form = self.form_obj
        # change
        if self.form_obj.is_valid():
            gallery = self.form_obj.save()
            # 将 zip 文件解压, 添加到相册中 , 并重命名文件
            try:
                if self.form_obj.cleaned_data['zip'] is not None:
                    zip = zipfile.ZipFile(self.form_obj.cleaned_data['zip'])
                    for filename in sorted(zip.namelist()):
                        file_name = os.path.basename(filename)
                        if not file_name:
                            continue
                        try:
                            data = zip.read(filename)
                            contentfile = ContentFile(data)
                            size = contentfile.size
                            if size < 1024:
                                logger.warning(f'small size photo({size}>1024 Bytes): "{filename}"')
                                continue
                            photo = Photo()
                            photo.gallery = gallery
                            newname = f'{gallery.uuid}{uuid.uuid4().hex[:10]}.jpg'
                            photo.title = newname
                            photo.image.save(newname, contentfile)
                            photo.thumb.save(f'thumb-{newname}', contentfile)
                        except Exception as e:
                            logger.error(e)
                        else:
                            photo.save()

                    zip.close()
            except:
                pass
            super().save_models()

    def form_valid(self, form):
        # form.instance.author = self.request.user  # 初始化表单数据
        return super().form_valid(form)

    def show_thumb_img(self, obj):
        '''展示封面'''
        url = obj.thumb.url
        return format_html(f'<img src="{url}" class="field_img">')
    show_thumb_img.short_description = '封面'  # 设置表头


    def block_extrabody(self, context, node):
        return lightense



@register(Photo)
class PhotoModelAdmin:
    list_display = ('id', 'title', 'description', 'gallery', 'create_date', 'is_delete', 'show_thumb_img')
    list_filter = ('gallery', 'create_date')
    exclude = ['thumb']
    ordering = ['-create_date']
    list_display_links = ['title']
    list_editable = ['is_delete']
    list_per_page = 20  # 每页显示20个

    def save_models(self):
        if self.form_obj.is_valid():
            try:
                img = self.form_obj.save(commit=False)
                uid = self.form_obj.cleaned_data['gallery'].uuid
                # 文件重命名
                filename = '{0}{1}.jpg'.format(uid, str(uuid.uuid4())[-13:])
                img.title = filename
                img.image.save(filename, self.form_obj.cleaned_data['image'])
                img.thumb.save('thumb-{0}'.format(filename), self.form_obj.cleaned_data['image'])
            except Exception as e:
                ...
            else:
                img.save()
                super().save_models()


    def show_thumb_img(self, obj):
        '''展示缩略图'''
        try:
            url = obj.thumb.url
            return format_html(f'<img src="{url}" class="field_img">')
        except Exception as e:
            logger.error(e)
            return 'null'
    show_thumb_img.short_description = '缩略图'  # 设置表头

    def block_extrabody(self, context, node):
        return lightense
