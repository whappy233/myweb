from apps.app_blog.models import Article
from .serializers import ArticleSerializer
from rest_framework.response import Response
from rest_framework.views import APIView


'''
DRF分页类
Django REST Framework提供了3种分页类:
    PageNumberPagination: 普通分页器.
        支持用户按?page=3&size=10这种更灵活的方式进行查询, 这样用户不仅可以选择页码, 还可以选择每页展示数据的数量.
        通常还需要设置 max_page_size 这个参数限制每页展示数据的最大数量, 以防止用户进行恶意查询(比如size=10000).

    LimitOffsetPagination: 偏移分页器.
        支持用户按?limit=20&offset=100这种方式进行查询.
        offset是查询数据的起始点, limit是每页展示数据的最大条数.
        通常还需要设置 max_limit 这个参数来限制展示给用户数据的最大数量.

    CursorPagination类: 加密分页器.
        这是DRF提供的加密分页查询, 仅支持用户按响应提供的上一页和下一页链接进行分页查询, 每页的页码都是加密的.
        使用这种方式进行分页需要你的模型有 'created' 这个字段, 否则你要手动指定 ordering 排序才能进行使用.
'''



'''
----------------------------------------------------------------------------------------
PageNumberPagination 类
'''
# DRF中使用默认分页类的最简单方式就是在settings.py中进行全局配置，如下所示：
REST_FRAMEWORK ={
    'DEFAULT_PAGINATION_CLASS':'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE':2
}
# 'GET v1/articles/?page=2'

# 但是如果你希望用户按 ?page=3&size=10 这种更灵活的方式进行查询，你就要进行个性化定制.
from rest_framework.pagination import PageNumberPagination
class MyPageNumberPagination(PageNumberPagination):
    '''自定义分页器'''
    page_size = 2   # 默认每页包含的数量
    page_size_query_param = 'size'  # ?page=5&size=10
    max_page_size = 10 # 每页包含的最大数量

    def get_paginated_response(self, data):
        # 重写get_paginated_response方法, 还可以改变响应数据的输出格式, 以及传递额外的内容.
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'results': data
        })

from rest_framework import viewsets
from .pagination import MyPageNumberPagination
# 在单个视图中使用
class ArticleViewSet(viewsets.ModelViewSet):
    ...
    pagination_class = MyPageNumberPagination  # 自定义分页器
    ...
# 在全局使用
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'app_api.pagination.MyPageNumberPagination',
}

# 'GET v1/articles/?page=2&size=10'


'''
----------------------------------------------------------------------------------------
LimitOffsetPagination 类
'''
# 全局配置
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
}
# 'GET v1/articles/?limit=2&offset=10'

# 自定义MyLimitOffsetPagination类
from rest_framework.pagination import LimitOffsetPagination
class MyLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 5   # default limit per age
    limit_query_param = 'limit'  # default is limit
    offset_query_param = 'offset'  # default param is offset
    max_limit = 10 # max limit per age



'''
----------------------------------------------------------------------------------------
CursorPagination 类

NOTE: 使用CursorPagination类需要你的模型里有created这个字段，否则你需要手动指定ordering字段。
      这是因为CursorPagination类只能对排过序的查询集进行分页展示.不过可以手动指定排序字段.
'''
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.CursorPagination',
    'PAGE_SIZE': 2
}

class MyPageNumberPagination(PageNumberPagination):
    '''自定义分页器'''
    page_size = 2   # 默认每页包含的数量
    page_size_query_param = 'page_size'  # ?page_size=2
    cursor_query_param = 'cursor'
    ordering = '-create_data'  # 手动指定按create_date排序






'''
函数类视图中使用分页类
NOTE: pagination_class 属性仅支持在 genericsAPIView 和视图集 viewset 中配置使用。
如果你使用函数或简单的 APIView 开发API视图, 那么你需要对你的数据进行手动分页，一个具体使用例子如下所示:
'''
from rest_framework.pagination import PageNumberPagination

class ArticleList0(APIView):
    """
    List all articles, or create a new article.
    """
    def get(self, request, format=None):
        articles = Article.objects.all()
        
        page = PageNumberPagination()  # 产生一个分页器对象
        page.page_size = 3  # 默认每页显示的多少条记录
        page.page_query_param = 'page'  # 默认查询参数名为 page
        page.page_size_query_param = 'size'  # 前台控制每页显示的最大条数
        page.max_page_size = 10  # 后台控制显示的最大记录条数
        
        ret = page.paginate_queryset(articles, request)
        serializer = ArticleSerializer(ret, many=True)
        return Response(serializer.data)