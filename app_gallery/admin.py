import os
import uuid
import zipfile
from django.contrib import admin
from django.core.files.base import ContentFile
from .models import Gallery, Photo
from .forms import GalleryForm
from uuid import uuid4


@admin.register(Gallery)
class GalleryModelAdmin(admin.ModelAdmin):
    form = GalleryForm
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('title', 'thumb', 'is_visible',
                    'create_date', 'mod_date', 'slug', 'is_delete')
    list_filter = ('create_date',)
    ordering = ['-mod_date']

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
    def save_model(self, request, obj, form, change):
        if form.is_valid():
            gallery = form.save()
            # 将 zip 文件解压, 添加到相册中 , 并重命名文件
            if form.cleaned_data['zip'] is not None:
                zip = zipfile.ZipFile(form.cleaned_data['zip'])
                for filename in sorted(zip.namelist()):
                    try:
                        file_name = os.path.basename(filename)
                        if not file_name:
                            continue

                        data = zip.read(filename)
                        contentfile = ContentFile(data)

                        img = Photo()
                        img.gallery = gallery
                        filename = '{0}{1}.jpg'.format(
                            gallery.slug[:8], str(uuid.uuid4())[-13:])
                        img.alt = filename
                        img.image.save(filename, contentfile)

                        img.thumb.save(
                            'thumb-{0}'.format(filename), contentfile)
                        img.save()
                    except Exception as e:
                        print('ERROR: ')
                        print(e)
                zip.close()
            super().save_model(request, obj, form, change)


@admin.register(Photo)
class PhotoModelAdmin(admin.ModelAdmin):
    list_display = ('alt', 'image', 'gallery', 'thumb',
                    'create_date', 'is_delete')
    list_filter = ('gallery', 'create_date')
    exclude = ['thumb']
    ordering = ['-create_date']

    def save_model(self, request, obj, form, change):
        if form.is_valid():
            img = form.save(commit=False)
            slug = form.cleaned_data['gallery'].slug
            # 文件重命名
            filename = '{0}{1}.jpg'.format(slug[:8], str(uuid.uuid4())[-13:])
            img.alt = filename
            img.image.save(filename, form.cleaned_data['image'])
            img.thumb.save('thumb-{0}'.format(filename),
                           form.cleaned_data['image'])
            img.save()
            super().save_model(request, obj, form, change)