import os


# 返回工程路径(myweb)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# 确保生产环境使用的密码并未用于其它环境，且未被提交至版本控制系统
SECRET_KEY = 'jh*9r+p97rvldfkdnm6yvnm(m&ws$x)=squ!=rlu5s(uilhj+g'
# Django文档建议不直接在settings.py里输入字符串
# SECRET_KEY= os.environ['SECRET_KEY']


# 不要在生产环境打开 debug 开关
DEBUG = True

ALLOWED_HOSTS = ['localhost', '*']

SITE_ID = 1  # 设置站点ID

# 在这里添加APP
# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',  # 管理员站点
    'django.contrib.auth',  # 认证授权系统
    'django.contrib.contenttypes',  # 内容类型框架
    'django.contrib.sessions',  # 会话框架
    'django.contrib.messages',  # 消息框架
    'django.contrib.staticfiles',  # 管理静态文件的框架

    'django.contrib.humanize',

    'app_user.apps.AppUserConfig',
    'app_blog.apps.AppBlogConfig',
    'app_sheet.apps.AppSheetConfig',
    'app_gallery.apps.AppGalleryConfig',
    'app_admin.apps.AppAdminConfig',

    'django.contrib.sites',  # 网站地图App1
    'django.contrib.sitemaps',  # 网站地图App2
    # 'django.contrib.postgres',

    'taggit',  # 第三方标签管理器
    'imagekit', # 第三方缩略图应用 pip install django-imagekit
    'ckeditor', # 第三方富文本编辑器 pip install django-ckeditor==6.0.0
    'ckeditor_uploader', # 第三方富文本编辑器_文件上传组件

]

# 中间件
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # 'django.middleware.http.SetRemoteAddrFromForwardedFor',  #  当部署在负载平衡proxy(如nginx)上, 该中间件用于获取用户实际的 ip 地址
    # x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')  # 获取真实ip
    # if x_forwarded_for: p = x_forwarded_for.split(',')[0]  # 所以这里是真实的ip
    # else: ip = request.META.get('REMOTE_ADDR')  # 这里获得代理ip
]

# 表示Python模块，定义程序的根URL路径
ROOT_URLCONF = 'myweb.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                # 自定义模版全局变量 Carlos (默认变量)
                'myweb.contexts.carlos',
            ],
        },
    },
]

WSGI_APPLICATION = 'myweb.wsgi.application'

# 数据库 mysql
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'blog',
#         'USER': 'root',
#         'PASSWORD': '********',
#         'port': '3306',
#         'host': 'localhost',
#     }
# }

# sqlite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# 缓存
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
        # 'KEY_FUNCTION': '对应的函数名'   # 生成key的函数（默认函数会生成为：【前缀:版本:key】）
    }
}



# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'  # 设置时区

USE_I18N = True  # 默认为True，是否启用自动翻译系统

USE_L10N = True  # 默认False，以本地化格式显示数字和时间

USE_TZ = False  # 默认值True。若使用了本地时间，必须设为False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
if DEBUG:
    STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'), ]
else:
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# 媒体文件
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR,'media')


LOGIN_REDIRECT_URL = 'app_blog:article_list'  # 如果请求中没有出现next参数, 在成功登陆后通知 Django 重定向到该地址
LOGIN_URL = 'app_user:login'  # 用户重定向并实现登陆的URL(例如使用login_required装饰器的视图)
LOGOUT_URL = 'app_user:logout'   # 用户重定向并实现退出登陆的URL

# 邮箱配置 #####################################################3
# EMAIL_HOST =  smtp.gmail.com      SMTP 服务器主机  默认localhost
# EMAIL_PORT = 587                  SMTP 端口 默认25
# EMAIL_HOST_USER = xxxx@gmail.com  SMTP 服务器用户名
# EMAIL_HOST_PASSEORD =  password   SMTP 服务器密码
# EMAIL_USE_TLS = True              是否采用 TLS 安全连接
# EMAIL_USE_SSL = False             是否采用隐式 TLS 安全连接
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # 输出到 Shell
AUTHENTICATION_BACKENDS = ('app_user.views.CustomBackend',)


# CkEditor 富文本编辑器配置
CKEDITOR_UPLOAD_PATH = 'blog_uploads/'  # 文件上传文件夹  media/blog_uploads/
CKEDITOR_JQUERY_URL ='https://apps.bdimg.com/libs/jquery/2.1.4/jquery.min.js'
CKEDITOR_IMAGE_BACKEND = 'pillow'
CKEDITOR_ALLOW_NONIMAGE_FILES = False
CKEDITOR_BROWSE_SHOW_DIRS = True
CKEDITOR_RESTRICT_BY_USER = False  # 如果为True /media/blog_uploads/用户名/ 
CKEDITOR_RESTRICT_BY_DATE = True  # /media/blog_uploads/用户名(CKEDITOR_RESTRICT_BY_USER 如果为True)/年/月/日/文件名
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': (['Source', '-',  'Preview', '-', ],
                    ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Print', 'SpellChecker', ],
                    ['Undo', 'Redo', '-', 'Find', 'Replace', '-', 'SelectAll', 'RemoveFormat', '-',
                     "CodeSnippet", 'Subscript', 'Superscript'],
                    ['NumberedList', 'BulletedList', '-', 'Blockquote'],
                    ['Link', 'Unlink', ],
                    ['Image', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar', ],
                    ['Format', 'Font', 'FontSize', 'TextColor', 'BGColor', ],
                    ['Bold', 'Italic', 'Underline', 'Strike', ],
                    ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
                    ),
        'extraPlugins': 'codesnippet',
        'width': 'auto',
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # 引擎（默认）
SESSION_COOKIE_NAME = "sessionid"  # Session的cookie保存在浏览器上时的key，
SESSION_COOKIE_PATH = "/"  # Session的cookie保存的路径（默认）
SESSION_COOKIE_DOMAIN = None  # Session的cookie保存的域名（默认）
SESSION_COOKIE_SECURE = False  # 是否Https传输cookie（默认）
SESSION_COOKIE_HTTPONLY = True  # 是否Session的cookie只支持http传输（默认）
SESSION_COOKIE_AGE = 60 * 30  # Session的cookie失效日期（30min）（默认）
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # 是否关闭浏览器使得Session过期（默认）
SESSION_SAVE_EVERY_REQUEST = True  # 是否每次请求都保存Session，默认修改之后才保存