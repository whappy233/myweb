from celery import Celery
from django.conf import settings
import os

# 第一步
# Celery

'''
1. 在与settings 同级路径下新建文件 clelry.py.
2. 在 APP 目录下创建文件 tasks.py.
3. 在视图中添加到任务.
4. 前台启动Celery, 在项目文件夹下面, "celery -A 项目名称 worker -P gevent(并发方式) -c 1000(并发数)
后台启动Celery: nohup celery -A 项目名称 worker -P gevent(并发方式) -c 1000(并发数) > celery.log 2 >&1
'''


# 设置配置
# BROKER_URL =  'amqp://username:password@localhost:5672/yourvhost'
# CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
# CELERY_TASK_SERIALIZER = 'msgpack'
# CELERY_RESULT_SERIALIZER = 'msgpack'
# CELERY_TASK_RESULT_EXPIRES = 60 * 60 * 24
# CELERY_ACCEPT_CONTENT = ["msgpack"]
# CELERY_DEFAULT_QUEUE = "default"   
# CELERY_QUEUES = {
#     "default": { # 这是上面指定的默认队列
#         "exchange": "default",
#         "exchange_type": "direct",
#         "routing_key": "default"
#     }
# }

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myweb.settings')

app = Celery('test_celery', 
                broker='redis://127.0.0.1:6379/1', 
                backend='redis://127.0.0.1:6379/2')
app.autodiscover_tasks(settings.INSTALLED_APPS)  # 设置APP自动加载任务
