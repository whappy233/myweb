
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'myweb',
        'USER': 'root',
        'PASSWORD': '******',
        'PORT': '3306',
        'HOST': 'localhost',
        # 'CONN_MAX_AGE': 0,  # 数据库连接的生命周期，默认为0请求结束时关闭数据库，设置为None无限持久连接
        # 设置mysql启用严格模式, 不指定会有警告信息
        # 'OPTIONS': {'init_command':"SET sql_mode='STRICT_TRANS_TABLES'"},
        # TIME_ZONE:设置时区
        # DISABLE_SERVER_SIDE_CURSORS：True时禁用服务器端游标
    }
}


CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379', # redis所在服务器或容器ip地址
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": '*******', # 你设置的密码
        },
    },
}



# 邮箱配置
EMAIL_HOST =  'smtp.qq.com'             # SMTP 服务器主机  默认localhost
EMAIL_PORT = 465                        # SMTP 端口 默认25
EMAIL_HOST_USER = 'me@meetagain.top'    # SMTP 服务器用户名
EMAIL_HOST_PASSWORD = '*******'        # SMTP 服务器密码
# EMAIL_USE_TLS / EMAIL_USE_SSL 是互斥的，因此只能将这些设置之一设置为True。
# EMAIL_USE_TLS = True                  # 是否采用 TLS 安全连接
EMAIL_USE_SSL = True                    # 是否采 SSL 安全连接
EMAIL_SUBJECT_PREFIX = '[星海StarSea]'   # 邮件标题前缀,默认是'[django]'

