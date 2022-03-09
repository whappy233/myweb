
from django.core.paginator import Paginator
from django.template.response import TemplateResponse
from django.utils.decorators import classonlymethod

from django.views.generic import ListView, DetailView, CreateView



class MyListView(ListView):

    # 所有属性
    allow_empty = True                  # 允许结果为空
    content_type = None                 # 内容类型
    context_object_name = None          # 模板上下文名称, 默认:模型名称_list
    extra_context = None                # 要传递的额外上下文信息 dict
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace']
    model = None                        # 关联的模型
    ordering = None                     # 排序 str|list
    page_kwarg = 'page'                 # URL中页码关键字
    paginate_by = None                  # 每页对象的个数
    paginate_orphans = 0                #
    paginator_class = Paginator         # 分页处理类
    queryset = None                     # 关联的结果集
    response_class = TemplateResponse   # response 处理程序
    template_engine = None              # 模板引擎
    template_name = None                # 模板名称
    template_name_suffix = '_list'      # 

    def __init__(self, **kwargs):...
    def _allowed_methods(self):...                                      # 允许的请求方法. list
    @classonlymethod
    def as_view(cls, **init_kwargs):...                                 # 请求入口
    def dispatch(self, request, *args, **kwargs):...                    # 分派处理方法
    def get(self, request, *args, **kwargs):...                         # 可以为 get, post, put, patch, delete, head, trace 等请求
    def get_allow_empty(self):...                                       # 如果视图应该显示空列, 则返回 True, 如果应该引发 404, 则返回False. Bool
    def get_context_data(self, **kwargs):...                            # 传入到模板的 context
    def get_context_object_name(self, object_list):...                  # 获取模板上下文名称. str
    def get_ordering(self):...                                          # 获取排序的字段
    def get_paginate_by(self, queryset):...                             # 获取每页对象的个数. int/None
    def get_paginate_orphans(self):...                                  # 
    def get_paginator(self, queryset, per_page, orphans=0, allow_empty_first_page=True, **kwargs):...  # 返回分页器实例. Paginator(...)
    def get_queryset(self):...                                          # 返回此视图的项目列表. 返回值必须是iterable, 并且可以是'QuerySet'的实例, 在这种情况下, 将启用'QuerySet'特定行为. 
    def get_template_names(self):...                                    # 返回用于请求的模板名称列表.
    def http_method_not_allowed(self, request, *args, **kwargs):...     # 不允许的请求方法时, return HttpResponseNotAllowed(...)
    def options(self, request, *args, **kwargs):...                     # 处理 options 请求
    def paginate_queryset(self, queryset, page_size):...                # 如果需要,则对查询集进行分页
    def render_to_response(self, context, **response_kwargs):...        # 使用 response_class 返回一个响应，并使用给定上下文呈现的模板。将 response_kwargs 传递给 response 类的构造函数。
    def setup(self, request, *args, **kwargs):...                       # 初始化 request, args, kwargs


class MyDetailView(DetailView):

    # 所有属性
    content_type = None                 # 内容类型
    context_object_name = None          # 模板上下文名称, 默认:模型名称_list
    extra_context = None                # 要传递的额外上下文信息 dict
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace']
    model = None                        # 关联的模型
    pk_url_kwarg = 'pk'                 # 模型主键字段名称
    query_pk_and_slug = False           # 
    queryset = None                     # 关联的结果集
    response_class = TemplateResponse   # response 处理程序
    slug_field = 'slug'                 # 模型slug字段的名称
    slug_url_kwarg = 'slug'             # URL 中 slug 名称
    template_engine = None              # 模板引擎
    template_name = None                # 模板名称
    template_name_field = None          # 
    template_name_suffix = '_detail'    # 

    def __init__(self, **kwargs):...
    def _allowed_methods(self):...                                      # 允许的请求方法. list
    @classonlymethod
    def as_view(cls, **init_kwargs):...                                 # 请求入口
    def dispatch(self, request, *args, **kwargs):...                    # 分派处理方法
    def get(self, request, *args, **kwargs):...                         # 可以为 get, post, put, patch, delete, head, trace 等请求
    def get_context_data(self, **kwargs):...                            # 传入到模板的 context
    def get_context_object_name(self, obj):...                          # 获取模板上下文名称. str
    def get_object(self, queryset=None):...                             # 返回视图正在显示的对象。在URLconf中需要'self.queryset'和'pk'或'slug'参数。子类可以重写此参数以返回任何对象。
    def get_queryset(self):...                                          # 返回将用于查找对象的'QuerySet'。此方法由 get_object（）的默认实现调用，如果覆盖get_object（），则可能不会调用此方法。
    def get_slug_field(self):...                                        # 获取slug用于查找的slug字段的名称。
    def get_template_names(self):...                                    # 返回用于请求的模板名称列表.
    def http_method_not_allowed(self, request, *args, **kwargs):...     # 不允许的请求方法时, return HttpResponseNotAllowed(...)
    def options(self, request, *args, **kwargs):...                     # 处理 options 请求
    def render_to_response(self, context, **response_kwargs):...        # 使用 response_class 返回一个响应，并使用给定上下文呈现的模板。将 response_kwargs 传递给 response 类的构造函数。
    def setup(self, request, *args, **kwargs):...                       # 初始化 request, args, kwargs


class MyCreateView(CreateView):
    # 所有属性
    content_type = None                 # 内容类型
    context_object_name = None          # 模板上下文名称, 默认:模型名称_list
    extra_context = None                # 要传递的额外上下文信息 dict
    fields = None                       # 
    form_class = None                   # 关联的表单类
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace']
    initial = {}                        # 
    model = None                        # 关联的模型
    pk_url_kwarg = 'pk'                 # URL 中代表主键的名称
    prefix = None                       # 
    query_pk_and_slug = False           # 
    queryset = None                     # 关联的结果集
    response_class = TemplateResponse   # 
    slug_field = 'slug'                 # 模型中的 slug 字段
    slug_url_kwarg = 'slug'             # URL 中代表slug的名称
    success_url = None                  # 成功后跳转的 URL 地址
    template_engine = None              # 模板引擎
    template_name = None                # 模板名称
    template_name_field = None          # 
    template_name_suffix = '_form'      # 

    def _allowed_methods(self):...                                      # 
    @classonlymethod
    def as_view(cls, **initkwargs):...                                  # 
    def dispatch(self, request, *args, **kwargs):...                    # 
    def form_invalid(self, form):...                                    # 表单验证失败, render 无效的表单
    def form_valid(self, form):...                                      # 验证成功, 保存到数据库, 跳转到 success_url
    def get(self, request, *args, **kwargs):...                         # 处理get请求
    def get_context_data(self, **kwargs):...                            # 
    def get_context_object_name(self, obj):...                          # 
    def get_form(self, form_class=None):...                             # 返回表单实例
    def get_form_class(self):...                                        # 
    def get_form_kwargs(self):...                                       # 
    def get_initial(self):...                                           # 
    def get_object(self, queryset=None):...                             # 
    def get_prefix(self):...                                            # 
    def get_queryset(self):...                                          # 
    def get_slug_field(self):...                                        # 
    def get_success_url(self):...                                       # 
    def get_template_names(self):...                                    # 
    def http_method_not_allowed(self, request, *args, **kwargs):...     # 
    def __init__(self, **kwargs):...                                    # 
    def options(self, request, *args, **kwargs):...                     # 
    def post(self, request, *args, **kwargs):...                        # 处理 post 请求
    def put(self, *args, **kwargs):...                                  # 
    def render_to_response(self, context, **response_kwargs):...        # 
    def setup(self, request, *args, **kwargs):...                       #