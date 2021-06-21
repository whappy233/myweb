
from django.conf import settings
from django.core.paginator import Paginator
from django.http.response import HttpResponse
from haystack.views import SearchView


class MySearchView(SearchView):
    template = 'tp/search.html'

    def build_page(self):
        print('进入搜索页面: ')
        # 分页重写
        context = super(MySearchView, self).extra_context()  # 继承自带的context
        try:
            page_num = int(self.request.GET.get('page', 1))
        except Exception:
            return HttpResponse("页码无效.")
        if page_num < 1:
            return HttpResponse("页码应该大于等于1")
        a = []
        for i in self.results:
            a.append(i.object)
        paginator = Paginator(a, settings.HAYSTACK_SEARCH_RESULTS_PER_PAGE)
        page = paginator.page(page_num)
        print('搜索的信息: ', page)
        return (paginator, page)

    def extra_context(self):
        '''重载extra_context来添加额外的context内容'''

        context = super(MySearchView, self).extra_context()
        context['title'] = '搜索'
        return context
