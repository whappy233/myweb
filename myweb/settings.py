import os
import sys
from loguru import logger
from django.utils import timezone


def env_to_bool(env, default):
    str_val = os.environ.get(env)
    return default if str_val is None else str_val == 'True'


# 返回工程路径(myweb)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 添加 apps 目录
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# 确保生产环境使用的密码并未用于其它环境，且未被提交至版本控制系统
# Django文档建议不直接在settings.py里输入字符串
SECRET_KEY = os.environ['SECRET_KEY']

# 不要在生产环境打开 debug 开关
DEBUG = os.environ.get('USER_NAME') == 'Carlos'

ALLOWED_HOSTS = ['*']

SITE_ID = 1  # 设置站点ID

# INTERNAL_IPS = ['127.0.0.1',]  # django-debug-toolbar

INSTALLED_APPS = [
    'django.contrib.admin',         # 管理员站点
    'django.contrib.auth',          # 认证授权系统
    'django.contrib.contenttypes',  # 内容类型框架
    'django.contrib.sessions',      # 会话框架
    'django.contrib.messages',      # 消息框架
    'django.contrib.staticfiles',   # 管理静态文件的框架

    'django.contrib.humanize',      # 数字,日期人性化格式
    'django.contrib.sites',         # 网站地图App1
    'django.contrib.sitemaps',      # 网站地图App2

    'rest_framework',

    'haystack',    # django 搜索框架, haystack 要放在被搜索的应用的上面

    'app_user.apps.AppUserConfig',
    'app_blog.apps.AppBlogConfig',
    'app_gallery.apps.AppGalleryConfig',
    'app_common.apps.AppCommonConfig',
    'app_comments.apps.AppCommentsConfig',
    'app_diary.apps.AppDiaryConfig',
    'app_api.apps.AppApiConfig',

    'taggit',                       # 第三方标签管理器
    'imagekit',                     # 第三方缩略图应用 pip install django-imagekit
    # 'ckeditor',                   # 第三方富文本编辑器 pip install django-ckeditor==6.0.0
    # 'ckeditor_uploader',          # 第三方富文本编辑器_文件上传组件

    'mdeditor',                     # 第三方富文本编辑器

    # 'debug_toolbar',              # django-debug-toolbar
    'mptt',                         # 使Django项目能在数据库中存储层次结构(树形数据)的技术, 它可以让相关操作更加高效. 主要实现了修改过的前序遍历算法

    # xadmin 模块
    'xadmin',
    'crispy_forms',
    'reversion',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.cache.UpdateCacheMiddleware', # 缓存整个站点, 必须放在列表首位
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.cache.FetchFromCacheMiddleware', # 缓存整个站点, 必须在最后一位
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # 在视图函数执行前向每个接收到的user对象添加HttpRequest属性，表示当前登录的用户
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # 'app_user.middleware.front_user_middleware',
    # 'app_user.middleware.FrontUserMiddleware',
    'app_user.middleware.StatsMiddleware',

    # 全站缓存
    # 'django.middleware.cache.UpdateCacheMiddleware',
    # 'django.middleware.common.CommonMiddleware',
    # 'django.middleware.cache.FetchFromCacheMiddleware'

    # 'debug_toolbar.middleware.DebugToolbarMiddleware',  # django-debug-toolbar

    'app_common.middleware.CommonMiddleware',
]

# 表示Python模块，定义程序的根URL路径
ROOT_URLCONF = 'myweb.urls'

# 自定义验证后端,实现用户名邮箱手机号登录
AUTHENTICATION_BACKENDS = ('app_user.user_login_backend.CustomBackend',)

WSGI_APPLICATION = 'myweb.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # 定义目录列表，引擎应在其中按搜索顺序查找模板源文件
        'APP_DIRS': True,  # 直接在app的目录下寻找templates
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',   # 在模板中可以直接使用request对象
                'django.contrib.auth.context_processors.auth',  # 在模板里面可以直接使用user，perms对象
                'django.contrib.messages.context_processors.messages',  # 在模板里面可以直接使用message对象

                # 其他
                # django.template.context_processors.i18n   在模板里面可以直接使用 settings 的 LANGUAGES 和 LANGUAGE_CODE
                # django.template.context_processors.media  可以在模板里面使用 settings 的 MEDIA_URL 参数
                # django.template.context_processors.csrf   给模板标签 {% csrf_token %} 提供 token 值，默认总是开启。
                # django.template.context_processors.tz     可以在模板里面使用 TIME_ZONE 参数

                # 自定义模版全局变量 Carlos (默认变量)
                'myweb.contexts.carlos',

                'app_blog.context_processors.contexts',
                'app_diary.context_processors.contexts',

                'app_common.context_processors.seo_processor',

                'app_gallery.context_processors.contexts',
            ],
        },
    },
]

# ------------------------------------------------------------------------------------
# 使用 jinja2 模板引擎
# TEMPLATES_jinja2 = [
#     {
#         'BACKEND': 'django.template.backends.jinja2.Jinja2',
#         'DIRS': [os.path.join(BASE_DIR, 'templates')],  # 定义目录列表，引擎应在其中按搜索顺序查找模板源文件
#         'APP_DIRS': True,  # 告诉引擎是否在已安装的应用程序中寻找模板
#         'OPTIONS': {
#             'context_processors': [
#                 'django.template.context_processors.debug',
#                 'django.template.context_processors.request',
#                 'django.contrib.auth.context_processors.auth',
#                 'django.contrib.messages.context_processors.messages',
#             ],
#             'environment': 'learning_logs.jinja2_env.environment',  # 添加环境变量
#         },
#     },
# ]

# ------------------------------------------------------------------------------------
# jinja2_env.py

# from django.templatetags.static import static
# from django.urls import reverse
# from jinja2 import Environment

# def environment(**options):
#     env = Environment(**options)
#     env.globals.update({
#         'static': static,
#         'url': reverse,
#     })
#     return env
# ------------------------------------------------------------------------------------
# <img src="{{ static('path/to/company-logo.png') }}" alt="Company Logo">
# <a href="{{ url('admin:index') }}">Administration</a>
# ------------------------------------------------------------------------------------


# 数据库 mysql
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
# 'django.db.backends.postgresql'
# 'django.db.backends.mysql'
# 'django.db.backends.sqlite3'
# 'django.db.backends.oracle
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'blog',
#         'USER': 'root',
#         'PASSWORD': '********',
#         'PORT': '3306',
#         'HOST': 'localhost',
#         # 'CONN_MAX_AGE': 0,  # 数据库连接的生命周期，默认为0请求结束时关闭数据库，设置为None无限持久连接
#         # 设置mysql启用严格模式, 不指定会有警告信息
#         # 'OPTIONS': {'init_command':"SET sql_mode='STRICT_TRANS_TABLES'"},
#         # TIME_ZONE：设置时区
#         # DISABLE_SERVER_SIDE_CURSORS：True时禁用服务器端游标
#     }
# }
# migrate管理命令会同时在每一个数据库上运行，默认情况下它在default数据库上运行 ，
# 可以通过选项 --database 来指定需要同步的数据库。如不指定会同步到default数据库上.
# python manage.py migrate   #同步默认数据库
# python manage.py migrate --database=db1
# python manage.py migrate --database=db2


# sqlite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# 日志文件配置
LOG_DIR = os.path.join(BASE_DIR, 'log')
if not os.path.exists(LOG_DIR): 
    os.makedirs(LOG_DIR)
logger.add(os.path.join(LOG_DIR, 'django_error.log'),  # 日志存放路径
           enqueue=True,        # 开启进程安全
           rotation='1 days',   # 日志按天滚动
           retention='30 days', # 日志保留天数
           encoding='utf-8',    # 编码方式
           backtrace=True, diagnose=True,        # 开启错误堆栈
           level='INFO' if DEBUG else 'WARNING', # 日志级别
           )



# 缓存
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.dummy.DummyCache', # 引擎 (开发调试缓存)
#         'TIMEOUT': 300, # 缓存超时时间（默认300，None表示永不过期，0表示立即过期）
#         'OPTIONS':{
#             'MAX_ENTRIES': 300, # 最大缓存个数（默认300）
#             'CULL_FREQUENCY': 3, # 缓存到达最大个数之后，剔除缓存个数的比例，即：1/CULL_FREQUENCY（默认3）
#         },
#         'KEY_PREFIX': '',  # 缓存key的前缀（默认空）
#         'VERSION': 1, # 缓存key的版本（默认1）
#         # 'KEY_FUNCTION': '对应的函数名'   # 生成key的函数（默认函数会生成为：【前缀:版本:key】）
#     }
# }


# Redis 缓存
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379', # redis所在服务器或容器ip地址
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": os.environ.get('REDIS_KEYS') or '123456', # 你设置的密码
        },
    },
}
REDIS_TIMEOUT = 24*60*60
CUBES_REDIS_TIMEOUT = 60*30
NEVER_REDIS_TIMEOUT = 365*24*60*60


# CACHE_CONTROL_MAX_AGE = 2592000
# CACHES = {
#     'default': {
#         # 此缓存使用 python-memcached 模块连接 memcache
#         'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#         'LOCATION': os.environ.get('REDIS_KEYS') or '127.0.0.1:11211',
#         'KEY_PREFIX': 'djangoblog', # 缓存key的前缀（默认空）
#         'TIMEOUT': 15,
#     } if env_to_bool('DJANGO_MEMCACHED_ENABLE', False) else {
#         'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#         'TIMEOUT': 10800,
#         'LOCATION': 'unique-snowflake',
#     }
# }


LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'  # 设置时区
USE_I18N = True  # 默认为True，是否启用自动翻译系统
USE_L10N = True  # 默认False，以本地化格式显示数字和时间
USE_TZ = False  # 默认值True。若使用了本地时间，必须设为False


# 静态文件
STATIC_URL = '/static/'
if DEBUG:
    STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'), ]
else:
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# 媒体文件
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR,'media')


# 如果请求中没有出现next参数, 在成功登陆后通知 Django 重定向到该地址
LOGIN_REDIRECT_URL = 'app_blog:article_list'  
# 用户重定向并实现登陆的URL(例如使用login_required装饰器的视图)
LOGIN_URL = 'app_user:login'  
# 用户重定向并实现退出登陆的URL
LOGOUT_URL = 'app_user:logout'   


# djanho 搜索框架配置
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'myweb.whoosh_cn_backend.WhooshEngine',                   # 使用 Whoosh 引擎
        'PATH': os.path.join(os.path.dirname(__file__), 'whoosh_index'),    # 存放 Whoosh 索引文件的文件夹, python manage.py rebuild_index 生成的数据将存放在此
    },
}
# 设置每页显示的数目, 默认为20
HAYSTACK_SEARCH_RESULTS_PER_PAGE  =  8
# 每次数据库更新后自动更新索引
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'




# 邮箱配置
if DEBUG:  # 输出到 Shell
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST =  'smtp.qq.com'             # SMTP 服务器主机  默认localhost
EMAIL_PORT = 465                        # SMTP 端口 默认25
EMAIL_HOST_USER = os.environ.get('USER_EMAIL')              # SMTP 服务器用户名
EMAIL_HOST_PASSWORD = os.environ.get('USER_EMAIL_PW')       # SMTP 服务器密码
# EMAIL_USE_TLS / EMAIL_USE_SSL 是互斥的，因此只能将这些设置之一设置为True。
# EMAIL_USE_TLS = True                  # 是否采用 TLS 安全连接
EMAIL_USE_SSL = True                    # 是否采 SSL 安全连接
EMAIL_SUBJECT_PREFIX = '[星海StarSea]'   # 邮件标题前缀,默认是'[django]'


# CkEditor 富文本编辑器配置
# CKEDITOR_UPLOAD_PATH = 'blog_uploads/'  # 文件上传文件夹  media/blog_uploads/
# CKEDITOR_IMAGE_BACKEND = 'pillow'
# CKEDITOR_THUMBNAIL_SIZE = (300, 300)
# CKEDITOR_IMAGE_QUALITY = 40
# CKEDITOR_ALLOW_NONIMAGE_FILES = False
# CKEDITOR_BROWSE_SHOW_DIRS = True
# CKEDITOR_RESTRICT_BY_USER = False  # 如果为True /media/blog_uploads/用户名/
# CKEDITOR_RESTRICT_BY_DATE = True  # /media/blog_uploads/用户名(CKEDITOR_RESTRICT_BY_USER 如果为True)/年/月/日/文件名
# CKEDITOR_CONFIGS = {
#     'default': {
#         'toolbar': (['Source', '-',  'Preview', '-', ],
#                     ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Print', 'SpellChecker', ],
#                     ['Undo', 'Redo', '-', 'Find', 'Replace', '-', 'SelectAll', 'RemoveFormat', '-',
#                      "CodeSnippet", 'Subscript', 'Superscript'],
#                     ['NumberedList', 'BulletedList', '-', 'Blockquote'],
#                     ['Link', 'Unlink', ],
#                     ['Image', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar', ],
#                     ['Format', 'Font', 'FontSize', 'TextColor', 'BGColor', ],
#                     ['Bold', 'Italic', 'Underline', 'Strike', ],
#                     ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
#                     ),
#         'extraPlugins': 'codesnippet',
#         'width': 'auto',
#     }
# }

# mdeditor 富文本编辑器配置
if timezone.now().hour >= 18:
    _mdeditor_theme = 'dark'
    _editor_theme = 'pastel-on-dark'
else:
    _mdeditor_theme = 'default'
    _editor_theme = 'default'
MDEDITOR_CONFIGS = {
'default':{
    'width': '90%',  # 自定义编辑框宽度
    'heigth': 500,   # 自定义编辑框高度
    'toolbar': ["undo", "redo", "|",
                "bold", "del", "italic", "quote", "ucwords", "uppercase", "lowercase", "|",
                "h1", "h2", "h3", "h5", "h6", "|",
                "list-ul", "list-ol", "hr", "|",
                "link", "reference-link", "image", "code", "preformatted-text", "code-block", "table", "datetime", "emoji", "html-entities", "pagebreak", "goto-line", "|",
                "help", "info", "||",
                "preview", "watch", "fullscreen"],  # 自定义编辑框工具栏
    'image_folder': 'body_imgs',        # 图片保存文件夹名称
    'upload_image_formats': ["jpg", "jpeg", "gif", "png", "bmp", "webp"],  # 图片上传格式类型
    'theme': _mdeditor_theme,           # 编辑框主题 ，dark / default
    'editor_theme': _editor_theme,      # edit区域主题，pastel-on-dark / default
    'preview_theme': _mdeditor_theme,   # 预览区域主题， dark / default
    'tex': True,                        # 是否开启 tex 图表功能
    'emoji': True,                      # 是否开启表情功能
    'watch': True,                      # 实时预览
    'sequence': True,                   # 是否开启序列图功能
    'flow_chart': True,                 # 是否开启流程图功能
    'lineNumbers': True,                # 行号
    'lineWrapping': False,              # 自动换行
    'search_replace': True,             # 是否开启查找替换
    'toolbar_autofixed': True,          # 工具栏是否吸顶
    }
}

# session 会话配置
# 'django.contrib.sessions.backends.db'
# 'django.contrib.sessions.backends.file'
# 'django.contrib.sessions.backends.cache'
# 'django.contrib.sessions.backends.cached_db'
# 'django.contrib.sessions.backends.signed_cookies'
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # 引擎（默认）
SESSION_COOKIE_NAME = "sessionid"  # Session的cookie保存在浏览器上时的key，
SESSION_COOKIE_PATH = "/"  # Session的cookie保存的路径（默认）
SESSION_COOKIE_DOMAIN = None  # Session的cookie保存的域名（默认） 
SESSION_COOKIE_AGE = 60 * 30  # Session的cookie失效日期（30min）（默认）
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # 是否关闭浏览器使得Session过期（默认）
SESSION_SAVE_EVERY_REQUEST = True  # 是否每次请求都保存Session，默认修改之后才保存


SESSION_COOKIE_SECURE = False  # 是否只有HTTPS连接才能发送cookie
SESSION_COOKIE_HTTPONLY = True  # 是否Session的cookie只支持http传输（默认）


# SECURITY安全设置 - 支持https时建议开启
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True # 将所有非SSL请求永久重定向到SSL
    SECURE_HSTS_SECONDS = 60
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True # 严格要求使用https协议传输
    SECURE_CONTENT_TYPE_NOSNIFF = True # 防止浏览器猜测资产的内容类型
    SESSION_COOKIE_SECURE = True # 仅通过https传输cookie
    CSRF_COOKIE_SECURE = True # 仅通过https传输cookie
    SECURE_HSTS_PRELOAD = True # HSTS为
    SECURE_FRAME_DENY = True  # 避免让自己的网页的框架和保护他们免受[点击劫持]
    SECURE_BROWSER_XSS_FILTER = True  # 启用浏览器的XSS过滤保护
    SESSION_COOKIE_HTTPONLY = True  # 防止COOKIE窃听，使客户端到服务端总是COOKIE加密传输
