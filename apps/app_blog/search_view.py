'''
haystack 搜索相关
'''

from django.http import JsonResponse
from django.shortcuts import render
from haystack.views import SearchView
from drf_haystack.viewsets import HaystackViewSet

from .search_serializers import ArticleIndexSerializer
from .models import Article


# https://blog.csdn.net/smartwu_sir/article/details/80209907



# /api/search/?text__contains=bug
# not__contains, startswith, endswith, =, 同样适用, page还有page_size选项
class ContentSearchViewSet(HaystackViewSet):

    # 这里可以写多个模型，相应的serializer 里也可以写多个 index_classes
    index_models = [Article]
    serializer_class = ArticleIndexSerializer



# /search/?q='关键字'
class MySearchView(SearchView):
    template = 'tp/搜索.html'

    def extra_context(self):
        '''重载extra_context来添加额外的context内容'''

        context = super(MySearchView, self).extra_context()
        context['title'] = '搜索'
        return context

    def create_response(self):  # 重载create_response来实现接口编写
        context = super().get_context()  # 搜索引擎完成后的内容
        # 'query': self.query  # 搜索的关键字
        # 'form': self.form
        # 'page': page
        # 'paginator': paginator
        # 'suggestion': None

        if not self.request.is_ajax():
            return render(self.request, self.template, context)

        keyword = self.request.GET.get('q', None)  # 关键子为q
        if not keyword:
            return JsonResponse({"status": {"code": 400, "msg": {"error_code": 4450, "error_msg": "关键字错误"}}})

        page = context['page']
        next_page = None
        if page.has_next():
            next_page = page.next_page_number()

        content = {"status": {"code": 200, "msg": "ok"}, "data": {"page": page.number, "next_page": next_page, "sort": '默认排序'}}
        content_list = []
        for i in page.object_list:  # 对象列表
            set_dict = {
                'id':      i.object.id, 
                'title':   i.object.title, 
                'summary': i.object.summary,
                'url':     i.object.get_absolute_url(),
            }
            content_list.append(set_dict)
        content["data"].update(dict(blog=content_list))

        return JsonResponse(content, json_dumps_params={'ensure_ascii':False})#对对象进行序列化返回json格式数据





