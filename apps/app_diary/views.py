from django.views.generic import ListView
from django.http.response import Http404, JsonResponse
from django.shortcuts import render
from django.core import serializers
from .models import Diary

from app_common.utils import JSONEncoder


class DiaryList(ListView):
    model = Diary
    paginate_by = 6
    template_name = 'tp/日记.html'
    context_object_name = 'diaries'
    # allow_empty = True

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()

        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if self.get_paginate_by(self.object_list) is not None and hasattr(self.object_list, 'exists'):
                is_empty = not self.object_list.exists()
            else:
                is_empty = not self.object_list
            if is_empty:
                raise Http404(_("Empty list and '%(class_name)s.allow_empty' is False.") % {
                    'class_name': self.__class__.__name__,
                })

        try:
            context = self.get_context_data()
        except Http404 as e:
            if request.is_ajax():
                print('数据为空')
                return JsonResponse({'status': 404, 'data':None})
            else:
                raise e


        if request.is_ajax():
            paginator = context['paginator']
            page_obj = context['page_obj']
            is_paginated = context['is_paginated']
            object_list = context['object_list']


            serialize_items = serializers.serialize("json", object_list, 
                    fields=('body', 'mood', 'img', 'updated'), 
                    ensure_ascii=False)

            data = {
                'status': 200,
                'current_page': page_obj.number,    # 当前页码
                'has_next': page_obj.has_next(),    # 是否有下页
                'page_total': paginator.num_pages,  # 总页数
                'items_count': paginator.count,     # 元素总数
                'data': serialize_items,
            }

            print(data)

            return JsonResponse(data)

        return self.render_to_response(context)



def details(request):
    return render(request, 'tp/日记.html')


47