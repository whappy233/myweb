from django.contrib import admin
from .models import Diary
from django.utils.html import format_html

# 日记
@admin.register(Diary)
class DiaryAdmin(admin.ModelAdmin):
    list_display = ['id', 'mood', 'body', 'slug', 'show_img', 'created', 'updated']
    search_fields = ['body', 'slug']
    list_filter = ['mood', 'created', 'updated' ]
    ordering = ['updated']
    list_display_links = ['id', 'mood', 'body', 'slug']

    def show_img(self, obj):
        '''展示配图'''
        try:
            url = obj.img.url
            return format_html(f'<img src="{url}" class="field_img">')
        except:
            return ''
    show_img.short_description = '配图'  # 设置表头