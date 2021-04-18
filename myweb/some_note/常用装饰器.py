'''权限验证'''


'''
=====================================================================
@login_required
'''
# @login_required 是 Django 最常用的一个装饰器。
# 其作用是在执行视图函数前先检查用户是否通过登录身份验证，并将未登录的用户重定向到指定的登录url。
# 其中login_url是可选参数。如果不设置，默认login_url是settings.py里设置的LOGIN_URL。
from django.contrib.auth.decorators import login_required
@login_required(login_url='/accounts/login/')
def my_view(request):
    ...

# @login_required 还可以一个可选参数是 redirect_field_name, 默认值是'next'。
@login_required(redirect_field_name='my_redirect_field')
def my_view(request):
    ...

# 注意:
# login_required 装饰器不会检查用户是否是 is_active 状态。
# 如果你想进一步限制登录验证成功的用户对某些视图函数的访问，你需要使用更强大的 @user_passes_test 装饰器。
# 使用基于类的视图时，可以使用 LoginRequiredMixin 实现和 login_required 相同的行为,
from django.contrib.auth.mixins import LoginRequiredMixin
# LoginRequiredMixin 应该在继承列表中最左侧的位置
class MyView(LoginRequiredMixin, View):
    '''未经验证用户的所有请求都会被重定向到登录页面或者显示 HTTP 403 Forbidden 错误，
    这取决于 raise_exception 参数'''
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    raise_exception = False  # 重定向到登录页面


from django.contrib.admin.views.decorators import staff_member_required
@staff_member_required  # 如果用户已登录, 且为工作人员, 且处于活动状态, 则正常执行视图



'''
=====================================================================
@user_passes_test
'''
# @user_passes_test 装饰器的作用是对登录用户对象的信息进行判断，只有通过测试(返回值为True)的用户才能访问视图函数。
# 不符合条件的用户会被跳转到指定的登录url
# @user_passes_test 装饰器有一个必选参数，即对用户对象信息进行判断的函数。
# 该函数必需接收user对象为参数。
# 与 @login_required 类似，@user_passes_test 还有两个可选参数(login_url和redirect_field_name)，这里就不多讲了。
# user_passes_test(func[,login_url=None, redirect_field_name=REDIRECT_FIELD_NAME])
# 下例 中@user_passes_test 装饰器对用户的email地址结尾进行判断，会把未通过测试的用户会定向到settings.LOGIN_URL。试想一个匿名用户来访问，她没有email地址，显然不能通过测试，登录后再来吧。
from django.contrib.auth.decorators import user_passes_test
def email_check(user):
    return user.email.endswith('@example.com')

@user_passes_test(email_check)
def my_view(request):
    ...
# 如果需要加可选参数，可以按如下方式使用。
@user_passes_test(email_check, login_url='/login/')
def my_view(request):
    ...
# 注意：
# @user_passes_test 不会自动的检查用户是否是匿名用户, 但是 @user_passes_test 装饰器还是可以起到两层校验的作用。
# 一来检查用户是否登录，二来检查用户是否符合某些条件，无需重复使用@login_required装饰器。
# 我们如果只允许 is_active 的登录用户访问某些视图，我们现在可以使用 @user_passes_test 装饰器轻松地解决这个问题，如下所示:
@user_passes_test(lambda u: u.is_active)
def my_view(request):
    ...


class UserPassesTestMixin
# 使用基于类的视图时，可以使用 UserPassesTestMixin 执行此操作。

# test_func()
# 你必须覆盖类方法 test_func() 以提供执行的测试。此外，还可以设置 AccessMixin 的任何参数来自定义处理未授权用户：
from django.contrib.auth.mixins import UserPassesTestMixin
class MyView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.email.endswith('@example.com')

# get_test_func()
# 你也可以覆盖 get_test_func() 方法，以使 mixin 对其检查使用不同名称的函数（而不是 test_func() ）。



'''
=====================================================================
@permission_required
'''
# @permission_required 装饰器的作用是检查用户用户是否有特定权限，第一个参数perm是权限名，为必选, 第二个参数login_url为可选。
# permission_required(perm[, login_url=None, raise_exception=False])
# 下例检查用户是否有 app_name.can_vote 的权限，没有的话定向至 login_url。如果你设置了 raise_exception=True, 会直接返回403无权限的错误，而不会跳转到登录页面。
# 那么问题来了，我们需要先使用@login_required来验证用户是否登录，再使用@permission_required装饰器来查看登录用户是否具有相关权限吗？ 
# 答案是不需要。如果一个匿名用户来访问这个视图，显然该用户没有相关权限，会自动定向至登录页面。
# 如果你想使用 raise_exception 但也想给用户登录的机会，那需要添加 login_required() 装饰器.
from django.contrib.auth.decorators import permission_required
@permission_required('app_name.can_vote', login_url='/login/')
def my_view(request):
    ...



from django.contrib.auth.mixins import PermissionRequiredMixin
class MyView(PermissionRequiredMixin, View):
    permission_required = 'polls.add_choice'
    # 或者提供多个权限
    # permission_required = ('polls.view_choice', 'polls.change_choice')





'''
=====================================================================
缓存
'''
# 缓存是Django装饰器很重要的一个应用场景。
# 下面我们来看几个主要的缓存装饰器。
# 注意: 使用以下装饰器的前提是你已经对缓存进行了相关设置

'@cache_page'
# 该装饰器可以接收缓存的时间作为参数，比如下例缓存页面15分钟。
from django.views.decorators.cache import cache_page
@cache_page(60 * 15)
def my_view(request):
    ...

'@cache_control'
# 通常用户将会面对两种缓存： 他或她自己的浏览器缓存（私有缓存）以及他或她的提供者缓存（公共缓存）。 
# 公共缓存由多个用户使用，而受其它人的控制。 
# 这就产生了你不想遇到的敏感数据的问题，比如说你的银行账号被存储在公众缓存中。 
# 因此，Web 应用程序需要以某种方式告诉缓存那些数据是私有的，哪些是公共的。cache_control 装饰器可以解决这个问题。
from django.views.decorators.cache import cache_control
@cache_control(private=True)
def my_view(request):
    ...
# 该修饰器负责在后台发送相应的 HTTP 头部。还有一些其他方法可以控制缓存参数。 例如, HTTP 允许应用程序执行如下操作:
# 定义页面可以被缓存的最大时间。
# 指定某个缓存是否总是检查较新版本，仅当无更新时才传递所缓存内容。
# 在 Django 中，可使用 cache_control 视图修饰器指定这些缓存参数。 
# 在下例中， cache_control 告诉缓存对每次访问都重新验证缓存并在最长 3600 秒内保存所缓存版本。
@cache_control(must_revalidate=True, max_age=3600)
def my_view(request):
    ...
# 在 cache_control() 中，任何合法的Cache-Control HTTP 指令都是有效的。下面是完整列表：
# public=True
# private=True
# no_cache=True
# no_transform=True
# must_revalidate=True
# proxy_revalidate=True
# max_age=num_seconds
# s_maxage=num_seconds

'vary_on_headers'
# 缺省情况下，Django 的缓存系统使用所请求的路径(如blog/article/1)来创建其缓存键。
# 这意味着不同用户请求同样路径都会得到同样的缓存版本，不考虑客户端user-agent, cookie和语言配置的不同,
#  除非你使用Vary头部通知缓存机制需要考虑请求头里的cookie和语言的不同。
# 要在 Django 完成这项工作，可使用便利的 vary_on_headers 视图装饰器。
# 例如下面代码告诉Django读取缓存数据时需要同时考虑User-Agent和Cookie的不同。与此类似的装饰器还有@vary_on_cookie。
# Vary 头定义了缓存机制在构建其缓存密钥时应该考虑哪些请求报头
from django.views.decorators.vary import vary_on_headers
@vary_on_headers('User-Agent', 'Cookie')
def my_view(request):
    ...


'@never_cache'  # 禁止浏览器缓存
# 如果你想用头部完全禁掉缓存, 你可以使用@never_cache装饰器。
# 如果你不在视图中使用缓存，服务器端是肯定不会缓存的，
# 然而用户的客户端如浏览器还是会缓存一些数据，这时你可以使用never_cache禁用掉客户端的缓存。
# 这个装饰器添加 Cache-Control: max-age=0, no-cache, no-store, must-revalidate 头到一个响应来标识禁止缓存该页面
from django.views.decorators.cache import never_cache
@never_cache
def myview(request):
    ...

'''
=====================================================================
其它常用装饰器
'''

'@method_decorator'
# 前面的案例中，我们的装饰器都是直接使用在函数视图上的。
# 如果需要在基于类的视图上使用装饰器，我们需要使用到 @method_decorator 这个装饰器, 
# 它的作用是将类伪装成函数方法。@method_decorator 第一个参数一般是需要使用的装饰器名。
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
@method_decorator(login_required, name='dispatch')
class ProtectedView(TemplateView):
    template_name = 'secret.html'

'@require_http_methods' # 该装饰器的作用是限制用户的请求方法。
# 与此类似的装饰器:
# require_GET()
# 装饰器可以要求视图只接受 GET 方法。用法如下：
# require_POST()
# 装饰器可以要求视图只接受 POST 方法。用法如下：
# require_safe()
# 装饰器可以要求视图只接收 GET 和 HEAD 方法。这些方法通常被认为是安全的，因为它们除了检索请求的资源外，没有特别的操作。
from django.views.decorators.http import require_http_methods
# 如下例中仅接收GET和POST方法。
@require_http_methods(["GET", "POST"])
def my_view(request):
    # Only accept GET or POST method
    pass

'@gzip_page'
# 该装饰器可以压缩内容，前提是用户客户端允许内容压缩的话.它相应的设置了 Vary 头部，这样缓存将基于 Accept-Encoding 头进行存储。
# 使用方法如下:
from django.views.decorators.gzip import gzip_page
@gzip_page
def my_view(request):
    # Only accept GET or POST method
    pass



'''
=====================================================================
使用多重装饰器
'''
# 你可以在一个函数或基于类的视图上使用多重装饰器，但一定要考虑装饰器执行的先后顺序。
# 比如下例中会先执行@never_cache, 再执行@login_required。

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
@method_decorator(never_cache, name='dispatch')
@method_decorator(login_required, name='dispatch')
class ProtectedView(TemplateView):
    template_name = 'secret.html'

# 上例等同于:
decorators = [never_cache, login_required]
@method_decorator(decorators, name='dispatch')
class ProtectedView(TemplateView):
    template_name = 'secret.html'