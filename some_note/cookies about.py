'''
Django中设置cookie以及获取cookie
设置cookie

 对 HttpResponse()对象的set_cookie方法进行设置  HttpResponse().set_cookie()

 第一个参数是 键名  第二参数是对应的值

 参数 max_age 设置过期时间，单位是秒

 参数 expires 设置到那个时间过期 日期类型
 
 '''

# 编写视图函数，进行设置
from datetime import datetime,timedelta
from django.http import HttpResponse
def set_cookie(request):
    """设置cookie"""
    response = HttpResponse("设置cookie")
    ''' max_age 设置过期时间，单位是秒 '''
    # response.set_cookie('name', 'tong', max_age=14 * 24 * 3600)
    ''' expires 设置过期时间，是从现在的时间开始到那个时间结束 '''
    response.set_cookie('name', 'tong', expires=datetime.now()+timedelta(days=14))
    return response


'''
获取cookie
利用request的request.COOKIES['键名']  来获取cookie
'''
# 视图函数中定义  get_cookie 方法
def get_cookie(request):
    """获取cookie"""
    name = request.COOKIES['name']
    return HttpResponse(name)


'''
删除Cookie
'''
response = HttpResponse('ok')
response.delete_cookie('hello')




'''
Cookie常用参数
key：键
value：值
max_age：多久后过期，时间为秒
expires：过期时间，为具体时间
path：生效路径
domain：生效的域名
secure：HTTPS传输时应设置为true
httponly：值应用于http传输，JavaScript无法获取
'''