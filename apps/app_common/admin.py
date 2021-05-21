from django.contrib import admin

# Register your models here.

from .models import BlogSettings, Carousel



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