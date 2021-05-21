LOGGING = {
    'version': 1,
    'filters': {  # 日志交由处理程序处理前需要满足的过滤条件(比如Debug=True或False)
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        }
     },
     'handlers': {  # 根据日志信息级别交由相应处理程序处理（比如生成文件或发送邮件）
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
         }
    },
    'loggers': {  # 生成和记录每条日志信息及级别
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        }
    }
}



LOG_DIR = os.path.join(BASE_DIR, "logs")        # 创建log文件的文件夹
ADMINS = (('admin_name', 'your@email.com'),)    # 给ADMINS发送邮件需要配置
MANAGERS = ADMINS
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,  # 表示是否禁用所有的已经存在的日志配置
    "filters": {        # 日志交由处理程序处理前需要满足的过滤条件(比如Debug=True或False)
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse"
        }
    },
    "formatters": {     # 定义了两种日志格式
        "verbose": {    # 标准
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"
        },
        'simple': {     # 简单
            'format': '[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d]%(message)s'
        },
    },
    "handlers": {       # 根据日志信息级别交由相应处理程序处理（比如生成文件或发送邮件）
        "mail_admins": {# 只有debug=False且Error级别以上发邮件给admin
            "level": "ERROR",
            "filters": ["require_debug_false"],     # DEBUG=False时记录
            "class": "django.utils.log.AdminEmailHandler",
        },
        'file_handler': {       # Info级别以上保存到日志文件
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',    # 保存到文件，根据文件大小自动切
            'filters': ["require_debug_false"],                 # DEBUG=False时记录
            'filename': os.path.join(LOG_DIR, "info.log"),      # 日志文件
            'maxBytes': 1024 * 1024 * 10,                       # 日志大小 10M
            'backupCount': 2,                                   # 备份数为 2
            'formatter': 'simple',                              # 简单格式
            'encoding': 'utf-8',
        },
        "console": {    # 打印到终端console
            'level': 'DEBUG',                       # 日志记录级别
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',                 # 日志格式选项
            'filters': ['require_debug_true'],      # DEBUG=True时记录
            # 'stream': 'ext://sys.stdout',   # 文件重定向的配置，将打印到控制台的信息都重定向出去 python manage.py runserver >> /home/aea/log/test.log
        },
    },
    "root": {
        "level": "INFO", 
        "handlers": ["console"]
    },
    "loggers": {                # 生成和记录每条日志信息及级别
        "django.request": {     # Django的request发生error会自动记录
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,  # 向不向更高级别的logger传递
        },
        "django.security.DisallowedHost": {  # 对于不在 ALLOWED_HOSTS 中的请求不发送报错邮件
            "level": "ERROR",
            "handlers": ["console", "mail_admins"],
            "propagate": True,
        },
    },
}
