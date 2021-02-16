from loguru import logger
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
            except Exception as e:
                logger.error(e)
                request.front_user = None  # 避免发生异常时front_user对象没有绑定成功，从而在视图中发生报错
        else:
            request.front_user = None  # 避免以后用户没有登录的情况下报错

        # 在调用视图（和随后的中间件）之前，将为每个请求执行的代码。
        response = get_response(request)
        # 调用视图后将为每个请求/响应执行的代码

        print('response到达浏览器之前执行的代码...')
        return response

    return middleware


import time
class StatsMiddleware(object):
    def __init__(self, get_response):
        # 执行一些初始代码 
        self.get_response = get_response

    def __call__(self,request):
        s = time.time()
        response = self.get_response(request)
        o = time.time() - s
        try:
            response.content = response.content.replace(b'<!!LOAD_TIMES!!>', str(o)[:5].encode())
        except:
            logger.error(f'不支持的 content 类型: "{type(response)}"')
            print(f'不支持的 content 类型: "{type(response)}"')
        return response
        # response["X-total-time"] = int(total * 1000)

    def process_view(self, request, view_func, view_args, view_kwargs):
        return None

    def process_response(self, request, response):
        return response

    def process_request(self, request):
        print(4444444444444444444)


# 2. 类实现中间件
from django.contrib.auth.models import User
class FrontUserMiddleware(object):
    def __init__(self, get_response):
        # 执行一些初始代码
        print('FrontUserMiddleware 中间件初始化...')
        self.get_response = get_response

    def __call__(self,request):
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

        # 在调用视图（和随后的中间件）之前，将为每个请求执行的代码。
        response = self.get_response(request)
        # 调用视图后将为每个请求/响应执行的代码
        print('response到达浏览器之前执行的代码...')

        return response



# 3. 即将被遗弃的一个中间件的定义方法≥
from django.utils.deprecation import MiddlewareMixin 
class FrontUserMiddleware3(MiddlewareMixin):
    def process_request(self, request):
        print("Request before view is called!")

    def process_response(self, request, response):
        print("Response after view is called!")
        return response

    def process_exception(self, request, exception):
        print("Exception!")

