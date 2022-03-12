

from .models import Diary
from django.utils.html import format_html
from django.urls import reverse
from xadmin.sites import register



lightense = '''
<script src="/static/st/js/lightense.min.js"></script>
<script>
$('#navbar-action').prepend('<a href="%s" class="btn btn-primary"> <i class="fa fa-eye"> 查看</i></a>')
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


# 日记
@register(Diary)
class DiaryAdmin:
    list_display = ('id', 'mood', 'body', 'slug', 'show_img', 'created', 'updated',)
    search_fields = ('body', 'slug',)
    list_filter = ['mood', 'created', 'updated' ]
    ordering = ('created',)
    list_display_links = ('id', 'mood', 'body', 'slug',)

    def show_img(self, obj):
        '''展示配图'''
        try:
            url = obj.img.url
            return format_html(f'<img src="{url}" class="field_img">')
        except:
            return ''
    show_img.short_description = '配图'  # 设置表头

    def block_extrabody(self, context, node):
        index_url = reverse('app_diary:index')
        return lightense%(index_url)
