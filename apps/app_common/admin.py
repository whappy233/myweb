from django.contrib import admin
from django.template.defaultfilters import filesizeformat

# Register your models here.

from .models import BlogSettings, Carousel, FileStorage



# 轮播图
@admin.register(Carousel)
class CarouselAdmin(admin.ModelAdmin):
    list_display = ['id', 'number', 'title', 'content', 'img_url', 'url']
    search_fields = ['title',]
    ordering = ['number', '-id'] 



# 网站配置
@admin.register(BlogSettings)
class BlogSettingsAdmin(admin.ModelAdmin):
    pass



# 文件管理
@admin.register(FileStorage)
class FileStorageAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'file', 'size', 'is_delete', 'created']
    list_display_links = ['id', 'name', 'file']
    list_editable = ['is_delete']
    ordering = ['-created']

    def save_model(self, request, obj, form, change):
        file = request.FILES['file']
        if not obj.name :
            obj.name = file.name
        obj.size = filesizeformat(file.size)
        obj.save()
