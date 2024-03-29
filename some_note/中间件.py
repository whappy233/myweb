

# 应用
# 禁止特定IP地址的用户或未登录的用户访问我们的View视图函数
# 对同一IP地址单位时间内发送的请求数量做出限制
# 在View视图函数执行前记录用户的IP地址
# 在View视图函数执行前传递额外的变量或参数
# 在View视图函数执行前或执行后把特定信息打印到log日志
# 在View视图函数执行后对reponse数据进行修改后返回给用户
# ...

#                              浏览器
#           (HttpRequest)       ↓ ↑       (HttpResponse)
#          -------------------- wsgi -------------------
#         |                                             ↑
#         ↓                                             |
# 中间件 process_request    --(response)-->    中间件 process_response
# -・-・-・-・-・-・-・- Request Exception Handler -・-・-・-・-・-・-・-・
#         ↓                      ↑                      ↑
#   URLConf (urls.py)            |            中间件 process_exception
#         ↓                      |
#     process_view     ----------
# -・-・-・-・-・-・-・- Views Exception Handler -・-・-・-・-・-・-・-・
#         |                      |
#         ↓                      |                       
#      views.py    <-------------⏌------------->    Template
#         ↓↑                                         ↑     ↑
#      models.py                                   filters tags
#         ↓↑
#      DATA BASES




# 1. 函数实现中间件
from django.contrib.auth.models import User
def front_user_middleware(get_response):
    # 执行一些初始代码
    print('front_user_middleware 中间件初始化...')
    def middleware(request):
        print('request到达views之前执行的代码...')
        user_id = request.session.get('user_id')
        if user_id:
            try:
                user = User.objects.get(pk=user_id)
                request.front_user = user
            except:
                request.front_user = None  # 避免发生异常时front_user对象没有绑定成功，从而在视图中发生报错
        else:
            request.front_user = None  # 避免以后用户没有登录的情况下报错

        # 当请求从浏览器发送到服务器时, 将调用 response = get_response(request) 该行之前的所有内容.
        # 当响应从服务器返回到浏览器时, 将调用 response = get_response(request) 此行之后的所有内容

        # 在调用视图（和随后的中间件）之前，将为每个请求执行的代码.
        # 请求在到达视图前执行的代码
        response = get_response(request)
        # 响应在返回给客户端前执行的代码
        # 调用视图后将为每个请求/响应执行的代码

        print('response到达浏览器之前执行的代码...')
        return response

    return middleware


# 检查处理请求的整个过程需要多长时间
import time
import datetime
def timing(get_response):
    def middleware(request):
        request.current_time = datetime.datetime.now()
        t1 = time.time()
        response = get_response(request)
        t2 = time.time()
        print("TOTAL_TIME:", (t2 - t1))
        return response
    return middleware


def simple_middleware(get_response):
    def middleware(request):
        # 这个方法什么也没做，我们只需要异常处理
        return get_response(request)

    def process_exception(request, exception):
        # Do something useful with the exception
        pass

    middleware.process_exception = process_exception
    return middleware


import requests
from django.http import HttpResponse
# Previous imports and timing middleware should remain unchanged
def stackoverflow(get_response):
    def middleware(request):
        # 这个方法什么也没做，我们只需要异常处理
        return get_response(request)

    def process_exception(request, exception):
        url = 'https://api.stackexchange.com/2.2/search'
        params = {
            'site': 'stackoverflow',
            'order': 'desc',
            'sort': 'votes',
            'pagesize': 3,
            'tagged': 'python;django',
            'intitle': str(exception),
        }
        response = requests.get(url, params=params)
        html = ''
        for question in response.json()['items']:
            html += '<h2><a href="{link}">{title}</a></h2>'.format(**question)
        return HttpResponse(html)

    middleware.process_exception = process_exception
    return middleware


# 2. 类实现中间件
from django.contrib.auth.models import User
from django.utils.decorators import decorator_from_middleware, decorator_from_middleware_with_args
# decorator_from_middleware 该方法将一个Middleware类转变为一个装饰器，可以用于单个视图函数上.
# decorator_from_middleware_with_args 与上一方法作用相同，只不过支持传递额外的参数
# cache_page = decorator_from_middleware_with_args(CacheMiddleware)
# @cache_page(3600)
# def my_view(request):
#     pass
class FrontUserMiddleware:
    def __init__(self, get_response):
        # 执行一些初始代码
        print('FrontUserMiddleware 中间件初始化...')
        self.get_response = get_response

    def __call__(self, request):
        print('request到达views之前执行的代码...')
        user_id = request.session.get('user_id')
        if user_id:
            try:
                user = User.objects.get(pk=user_id)
                request.front_user = user # 绑定当前登录的用户到request中去
            except:
                request.front_user = None  # 避免发生异常时front_user对象没有绑定成功，从而在视图中发生报错
        else:
            request.front_user = None  # 避免以后用户没有登录的情况下报错

        # 在调用视图（和随后的中间件）之前，将为每个请求执行的代码.

        response = self.get_response(request)

        # 调用视图后将为每个请求/响应执行的代码
        print('response到达浏览器之前执行的代码...')

        return response


    def process_view(self, request, view_func, view_args, view_kwargs):
        '''
        view_func: 简要使用的函数.
        它应该返回 None 或 HttpResponse 对象.
        如果它返回 None ，Django 将继续处理这个请求，执行任何其他的 process_view() ，然后执行相应的视图.
        如果它返回 HttpResponse 对象，Django 不会去影响调用相应的视图；它会将响应中间件应用到 HttpResponse 并返回结果.

        在视图运行前或在 process_view() 内访问中间件里的 request.POST 将阻止中间件之后运行的任何视图修改请求的上传处理程序 （modify the upload handlers for the request ），通常应该避免这样.
        '''
        ...

    def process_exception(self, request, exception):
        '''
        当视图引发异常时，Django 会调用 process_exception().
        process_exception() 应该返回 None 或 HttpResponse 对象.
        如果它返回一个 HttpResponse 对象，模板响应和响应中间件将被应用且会将结果响应返回浏览器.
        如果异常中间件返回一个响应，那么中间件之上的中间件类的 process_exception 方法根本不会被调用.
        否则，就会开始默认异常处理（ default exception handling ）.
        '''

        url = 'https://api.stackexchange.com/2.2/search'
        params = {
            'site': 'stackoverflow',
            'order': 'desc',
            'sort': 'votes',
            'pagesize': 3,
            'tagged': 'python;django',
            'intitle': str(exception),
        }
        response = requests.get(url, params=params)
        html = ''
        for question in response.json()['items']:
            html += '<h2><a href="{link}">{title}</a></h2>'.format(**question)
        return HttpResponse(html)

    def process_template_response(self, request, response):
        '''
        在视图被完全执行后调用，如果响应实例有 render() 方法，表明它是一个 TemplateResponse 或等效对象
        它必须返回一个实现了 render 方法的响应对象.
        它可以通过改变``response.template_name`` 和 response.context_data 来改变给定的 response ，或者它可以创建和返回全新的 TemplateResponse 或等效对象.
        '''
        return response

    # 处理流式响应
    # 与 HttpResponse 不同，StreamingHttpResponse 没有 content 属性.
    # 因此，中间件不能再假设所有响应有 content 属性.
    # 如果它们需要访问 content，它们必须为流式响应进行测试，并且调整其行为：

    if response.streaming:
        response.streaming_content = wrap_streaming_content(response.streaming_content)
    else:
        response.content = alter_content(response.content)

    # streaming_content 被假设为体积太大而无法在内存中保存.
    # 响应中间件可以将其包装在一个新的生成器里，但不能使用它.包装通常如下实现：
    def wrap_streaming_content(content):
        for chunk in content:
            yield alter_content(chunk)


# 3.
from django.utils.deprecation import MiddlewareMixin
class MyMiddleware(MiddlewareMixin):
    def __init__(self,get_response):
        # 执行一些初始代码
        print('MyMiddleware 中间件初始化...')
        super(MyMiddleware, self).__init__(get_response)

    def process_request(self,request):
        '''在进入 url 之前'''
        print('request到达views之前执行的代码...')
        user_id = request.session.get('user_id')
        if user_id:
            try:
                user = User.objects.get(pk=user_id)
                # 绑定当前登录的用户到request中去
                request.front_user = user
            except:
                # 避免发生异常时front_user对象没有绑定成功，从而在视图中发生报错
                request.front_user = None
        else:
            # 避免以后用户没有登录的情况下报错
            request.front_user = None

    def process_view(self, request, view_func, view_args, view_kwargs):
        '''
        在调用视图前被调用

        它应该返回 None 或 HttpResponse 对象.
        如果它返回 None ，Django 将继续处理这个请求，执行任何其他的 process_view() ，然后执行相应的视图.
        如果它返回 HttpResponse 对象，Django 不会去影响调用相应的视图；它会将响应中间件应用到 HttpResponse 并返回结果

        在视图运行前或在 process_view() 内访问中间件里的 request.POST 将阻止中间件之后运行的任何视图修改请求的上传处理程序，通常应该避免这样
        '''

        print('process_view')
        return None

    def process_template_response(self, request, response):
        '''
        request 是一个 HttpRequest 对象.response 是 TemplateResponse 对象（或者等效对象），它通过 Django 视图或中间件返回.
        process_template_response() 在视图被完全执行后调用，如果响应实例有 render() 方法，表明它是一个 TemplateResponse 或等效对象.
        它必须返回一个实现了 render 方法的响应对象.
        它可以通过改变``response.template_name`` 和 response.context_data 来改变给定的 response ，或者它可以创建和返回全新的 TemplateResponse 或等效对象.
        你不需要显式地渲染响应, 一旦所有模板中间件被调用，响应会被自动渲染.
        中间件会在响应阶段按照相反的顺序运行，其中包括 process_template_response() .
        '''

    def process_exception(self, request, exception):
        '''
        request 是一个 HttpRequest 对象. exception 是一个由视图函数引发的 Exception 对象.
        当视图引发异常时，Django 会调用 process_exception().

        process_exception() 应该返回 None 或 HttpResponse 对象.
        如果它返回一个 HttpResponse 对象，模板响应和响应中间件将被应用且会将结果响应返回浏览器.
        否则，就会开始默认异常处理（ default exception handling ）.

        再次，中间件在响应阶段会按照相反的顺序运行，其中包括 process_exception .
        如果异常中间件返回一个响应，那么中间件之上的中间件类的 process_exception 方法根本不会被调用.
        '''
        print("Exception!")

    def process_response(self, request, response):
        '''在返回到浏览器之前'''
        print("Response after view is called!")
        return response


