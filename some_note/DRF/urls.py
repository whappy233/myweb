'''
给URLs添加可选的格式后缀:
    为了充分利用我们的响应不再与单一内容类型连接,
    我们可以为API路径添加对格式后缀(.json或.api)的支持.
    使用格式后缀给我们明确指定了给定格式的 URL,
    能让我们的API将能够处理诸如 http://example.com/api/items/4.json之类的URL
'''
# 首先要给视图函数添加一个 format=None 关键字参数
def article_list(request, format=None):
    ...
def article_detail(request, pk, format=None):
    ...


from django.urls import re_path, path
from .views import ArticleListAPIView, ArticleDetailAPIView




urlpatterns = [
    # 函数视图
    path('articles/', article_list),
    path('articles/<int:pk>/', article_detail),

    # APIView 类视图
    path('articles/', ArticleListAPIView.as_view()),
    path('articles/<int:pk>/', ArticleDetailAPIView.as_view()),

]

# 在使用类视图时, 添加:
from rest_framework.urlpatterns import format_suffix_patterns
urlpatterns = format_suffix_patterns(urlpatterns)


