# Django 缓存



# 一. 缓存的配置  -----------------------------------------------
# 在 settings.py 中
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache', # 引擎 (开发调试缓存)
        'TIMEOUT': 300, # 缓存超时时间（默认300，None表示永不过期，0表示立即过期）
        'OPTIONS':{
            'MAX_ENTRIES': 300, # 最大缓存个数（默认300）                                      
            'CULL_FREQUENCY': 3, # 缓存到达最大个数之后，剔除缓存个数的比例，即：1/CULL_FREQUENCY（默认3）                                   
        },
        'KEY_PREFIX': '',  # 缓存key的前缀（默认空）
        'VERSION': 1, # 缓存key的版本（默认1）
        'KEY_FUNCTION': '对应的函数名'   # 生成key的函数（默认函数会生成为：【前缀:版本:key】）
    }
}

# 自定义key
def default_key_func(key, key_prefix, version):
    """
    Default function to generate keys.

    Constructs the key used by all other methods. By default it prepends
    the `key_prefix'. KEY_FUNCTION can be used to specify an alternate
    function with custom key making behavior.
    """
    return '%s:%s:%s' % (key_prefix, version, key)

def get_key_func(key_func):
    """
    Function to decide which key function to use.

    Defaults to ``default_key_func``.
    """
    if key_func is not None:
        if callable(key_func):
            return key_func
        else:
            return import_string(key_func)
    return default_key_func


# 不同 BACKEND 配置
# 1.此缓存将内容保存至数据库
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache', # 引擎
        'LOCATION': 'my_cache_table', # 需要缓存的数据库表
    }
}

# 2.此缓存将内容保存至文件
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/tmp/django_cache' # 文件位置,
    }
}

# 3.此缓存将内容保存至内存的变量中
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# 4.此缓存使用python-memcached模块连接memcache
CACHES = {  # localhost
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',  
    }
}
CACHES = {  # unix soket
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': 'unix:/tmp/memcached.sock',
    }
}   
CACHES = {  # 多个服务器上面的memcached
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': [
            '172.19.26.240:11211',
            '172.19.26.242:11211',
        ],
        # 我们也可以给缓存机器加权重，权重高的承担更多的请求，如下
        'LOCATION': [
            ('172.19.26.240:11211',5),
            ('172.19.26.242:11211',1),
        ]
    }
}

# 5.此缓存使用pylibmc模块连接memcache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
        'LOCATION': '设置的IP:设置的端口号',  
    }
}
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
        'LOCATION': '/tmp/memcached.sock',
    }
}   
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
        'LOCATION': [
            '设置的IP:设置的端口号',  
            '设置的IP:设置的端口号',  
        ]
    }
}

# 6.Redis 需要 pip3 install django-redis
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://设置的IP:设置的端口号",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {"max_connections": 100}
            # "PASSWORD": "密码",
        }
    }
}
from django_redis import get_redis_connection  # 视图中连接并操作
conn = get_redis_connection("default")




# 二. 缓存的使用  -----------------------------------------------

# 1.在视图View中使用cache
from django.views.decorators.cache import cache_page
@cache_page(60 * 15)
def my_view(request):
    pass

# 2.在路由URLConf中使用cache
from django.views.decorators.cache import cache_page
urlpatterns = [
    path('foo/<int:code>/', cache_page(60 * 15)(my_view)),]

# 3.在模板中使用cache
'''
{% load cache %}
{% cache 500 sidebar request.user.username %}
    .. sidebar for logged in user ..
{% endcache %}
'''



# 三. 缓存高级  -----------------------------------------------

### 使用 cache_control
# 通常用户将会面对两种缓存: 他或她自己的浏览器缓存（私有缓存）以及他或她的提供者缓存(公共缓存).
# 公共缓存由多个用户使用，而受其它人的控制. 
# 这就产生了你不想遇到的敏感数据的问题，比如说你的银行账号被存储在公众缓存中.
# 因此，Web 应用程序需要以某种方式告诉缓存那些数据是私有的，哪些是公共的.
# 解决方案是标示出某个页面缓存应当是私有的:
from django.views.decorators.cache import cache_control
@cache_control(private=True)  # 该修饰器负责在后台发送相应的 HTTP 头部
def my_view(request):
    pass

# cache_control() 中，任何合法的Cache-Control HTTP 指令都是有效的。下面是完整列表：
public=True
private=True            # 指定某个页面缓存应当是私有的
no_cache=True
no_transform=True
must_revalidate=True    # 指定某个缓存是否总是检查较新版本，仅当无更新时才传递所缓存内容
proxy_revalidate=True
max_age=3600            # 缓存保留时间
s_maxage=3600

### 使用 vary_on_headers
# 缺省情况下，Django 的缓存系统使用所请求的路径(如blog/post/1)来创建其缓存键。
# 这意味着不同用户请求同样路径都会得到同样的缓存版本，不考虑客户端user-agent, cookie和语言配置的不同, 
# 除非你使用Vary头部通知缓存机制需要考虑请求头里的cookie和语言的不同.
# 如下面代码告诉Django读取缓存数据时需要同时考虑User-Agent和Cookie的不同
from django.views.decorators.vary import vary_on_headers
@vary_on_headers('User-Agent', 'Cookie')
def my_view(request):
    pass

### 使用 naver_cache 禁用缓存
# 如果你想用头部完全禁掉缓存, 你可以使用django.views.decorators.cache.never_cache装饰器。
# 如果你不在视图中使用缓存，服务器端是肯定不会缓存的，
# 然而用户的客户端如浏览器还是会缓存一些数据，这时你可以使用never_cache禁用掉客户端的缓存。
from django.views.decorators.cache import never_cache
@never_cache
def myview(request):
    pass
