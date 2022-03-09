from __future__ import absolute_import
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

# 为 celery 命令行程序设置默认的 DJANGO_SETTINGS_MODULE 环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myweb.settings')


app = Celery('myweb')


# 大写名称空间意味着所有 Celery 配置选项必须以大写而不是小写指定, 并以 CELERY_开头.
# 因此例如 task_always_eager 设置变为 CELERY_TASK_ALWAYS_EAGER, broker_url 设置变为 CELERY_BROKER_URL
app.config_from_object('django.conf:settings', namespace='CELERY')


# 从所有已注册的 Django 应用程序中加载任务
app.autodiscover_tasks()  


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')