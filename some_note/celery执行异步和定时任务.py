'''
========================================================================
异步任务配置
'''

# 1.安装RabbitMQ，这里我们使用RabbitMQ作为broker，安装完成后默认启动了，也不需要其他任何配置
# apt-get install rabbitmq-server

# 2.安装celery
# pip3 install celery

# 3.celery用在django项目中，django项目目录结构(简化)如下
# website/
# |-- deploy
# |   |-- admin.py
# |   |-- apps.py
# |   |-- __init__.py
# |   |-- models.py
# |   |-- tasks.py
# |   |-- tests.py
# |   |-- urls.py
# |   `-- views.py
# |-- manage.py
# |-- README
# `-- website
#     |-- celery.py   # 和 setting.py 同目录下
#     |-- __init__.py
#     |-- settings.py
#     |-- urls.py
#     `-- wsgi.py


# 4.创建website/celery.py主文件
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery, platforms

# 为 'celery' 程序设置默认的Django设置模块。
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website.settings')

app = Celery('website')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# 从所有已注册的Django应用程序配置中加载任务模块。
app.autodiscover_tasks()

# 允许root 用户运行celery
platforms.C_FORCE_ROOT = True
@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

# 5.在website/__init__.py文件中增加如下内容，确保django启动的时候这个app能够被加载到
from __future__ import absolute_import
# 这将确保在Django启动时始终导入该应用，以便 shared_task 将使用此应用.
from .celery import app as celery_app
__all__ = ['celery_app']

# 6.各应用创建tasks.py文件，这里为deploy/tasks.py
from __future__ import absolute_import
from celery import shared_task
@shared_task
def add(x, y):
    return x + y
# 注意tasks.py必须建在各app的根目录下，且只能叫tasks.py，不能随意命名
@app.task
def XXX():  # 耗时任务
    for _ in range(5):
        time.sleep(1)
    print('ok')
    return '100'

# 7.views.py中引用使用这个tasks异步处理
from xxx_app.tasks import add
def post(request):
    result = add.delay(2, 3)
# 使用函数名.delay()即可使函数异步执行
# 可以通过result.ready()来判断任务是否完成处理
# 如果任务抛出一个异常，使用result.get(timeout=1)可以重新抛出异常
# 如果任务抛出一个异常，使用result.traceback可以获取原始的回溯信息

# 8.启动celery
# celery -A website worker -l info

# 9.这样在调用post这个方法时，里边的add就可以异步处理了


'''
========================================================================
定时任务配置
'''


# 1.website/celery.py 文件添加如下配置以支持定时任务
from celery.schedules import crontab
from datetime import timedelta
app.conf.update(
    CELERYBEAT_SCHEDULE = {
        'sum-task': {
            'task': 'xxx_app.tasks.add',
            # 每20秒执行
            'schedule':  timedelta(seconds=20),
            'args': (5, 6)  # 传输的参数
        },
        'send-report': {
            'task': 'xxx_app.tasks.report',
            # 每周一早上 4:30 执行
            'schedule': crontab(hour=4, minute=30, day_of_week=1),
        }
    }
)

# 定义了两个task:
# 名字为'sum-task'的task，每20秒执行一次add函数，并传了两个参数5和6
# 名字为'send-report'的task，每周一早上 4:30 执行 report 函数

# timedelta 对象参数:
    # days:天
    # seconds:秒
    # microseconds:微妙
    # milliseconds:毫秒
    # minutes:分
    # hours:小时

# crontab 的参数有：
#     month_of_year:月份
#     day_of_month:日期
#     day_of_week:周
#     hour:小时
#     minute:分钟


# 2. xxx_app/tasks.py文件:
from celery import shared_task
@shared_task
def add(x, y):
    return x + y

@shared_task
def report():
    return 5


# 3.启动celery beat，celery启动了一个beat进程一直在不断的判断是否有任务需要执行
# celery -A website beat -l info



# Tips:
# 如果你同时使用了异步任务和计划任务，有一种更简单的启动方式 celery -A website worker -b -l info，可同时启动worker和beat
# 如果使用的不是rabbitmq做队列那么需要在主配置文件中website/celery.py配置broker和backend，如下：

# redis做MQ配置
app = Celery('website', backend='redis', broker='redis://localhost')
# rabbitmq做MQ配置
app = Celery('website', backend='amqp', broker='amqp://admin:admin@localhost')

# celery不能用root用户启动的话需要在主配置文件中添加 platforms.C_FORCE_ROOT = True
# celery在长时间运行后可能出现内存泄漏，需要添加配置 CELERYD_MAX_TASKS_PER_CHILD = 10, 表示每个worker执行了多少个任务就死掉