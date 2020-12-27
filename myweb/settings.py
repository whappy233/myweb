import os


# 返回工程路径(myweb)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# 确保生产环境使用的密码并未用于其它环境，且未被提交至版本控制系统
SECRET_KEY = 'jh*9r+p97rvldfkdnm6yvnm(m&ws$x)=squ!=rlu5s(uilhj+g'

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

    'app_user.apps.AppUserConfig',
    'app_blog.apps.AppBlogConfig',
    'app_sheet.apps.AppSheetConfig',
    'app_gallery.apps.AppGalleryConfig',

    'taggit',  # 第三方标签管理器
    'django.contrib.sites',  # 网站地图App1
    'django.contrib.sitemaps',  # 网站地图App2
    # 'django.contrib.postgres',
    'imagekit', #  第三方缩略图应用 pip install django-imagekit
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

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False

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


LOGIN_REDIRECT_URL = 'app_blog:post_list'  # 如果请求中没有出现next参数, 在成功登陆后通知 Django 重定向到该地址
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