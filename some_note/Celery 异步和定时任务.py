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

# 为 'celery' 程序设置默认的Django 配置文件模块。
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website.settings')

app = Celery('website')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
# 这里指定从django的settings.py里读取celery配置
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动从所有已注册的django app中加载任务。
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
__all__ = ('celery_app',)

# 6.各应用创建tasks.py文件，这里为deploy/tasks.py
from __future__ import absolute_import
from celery import shared_task
import time
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

# 当我们使用 @app.task 装饰器定义我们的异步任务时，那么这个任务依赖于根据项目名myproject生成的Celery实例
# 然而我们在进行Django开发时为了保证每个app的可重用性，
# 我们经常会在每个app文件夹下编写异步任务，这些任务并不依赖于具体的Django项目名。
# 使用 @shared_task 装饰器能让我们避免对某个项目名对应 Celery 实例的依赖，使app的可移植性更强



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



'''
========================================================================
Tips:
'''
# 如果你同时使用了异步任务和计划任务，有一种更简单的启动方式 celery -A website worker -b -l info，可同时启动worker和beat
# 如果使用的不是 rabbitmq 做队列那么需要在主配置文件中 website/celery.py 配置 broker 和 backend，如下：

# redis做MQ配置
app = Celery('website', backend='redis', broker='redis://localhost')

# rabbitmq做MQ配置
app = Celery('website', backend='amqp', broker='amqp://admin:admin@localhost')

# celery不能用root用户启动的话需要在主配置文件中添加 platforms.C_FORCE_ROOT = True
# celery在长时间运行后可能出现内存泄漏，需要添加配置 CELERYD_MAX_TASKS_PER_CHILD = 10, 表示每个 worker 执行了多少个任务就死掉


# 如果异步的任务包括耗时的I/O操作
# 一个无限期阻塞的任务会使得工作单元无法再做其他事情。
# 如果你的任务里有 I/O 操作，请确保给这些操作加上超时时间，例如使用 requests 库时给网络请求添加一个超时时间：
connect_timeout, read_timeout = 5.0, 30.0
response = requests.get(URL, timeout=(connect_timeout, read_timeout))
# 默认的 prefork 池调度器对长时间任务不是很友好，所以如果你的任务需要运行很长时间，确保在启动工作单元时使能了 -ofair 选项


# 当使用多个装饰器装饰任务函数时，确保 task 装饰器最后应用（在python中，这意味它必须在第一个位置）：
@app.task
@decorator2
@decorator1
def add(x, y):
    return x + y


# 使用 bind=True 绑定任务
# 一个绑定任务意味着任务函数的第一个参数总是任务实例本身(self)，就像 Python 绑定方法类似，如下例所示：
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
@app.task(bind=True)
def add(self, x, y):
    logger.info(self.request.id)
# 绑定任务在这些情况下是必须的：任务重试（使用 app.Task.retry() )，访问当前任务请求的信息，以及你添加到自定义任务基类的附加功能


# 忽略不想要的结果
# 如果你不在意任务的返回结果，可以设置 ignore_result 选项，因为存储结果耗费时间和资源。
# 你还可以可以通过 task_ignore_result 设置全局忽略任务结果。
@app.task(ignore_result=True)
def mytask():
    something()


# 避免启动同步子任务
# 让一个任务等待另外一个任务的返回结果是很低效的，并且如果工作单元池被耗尽的话这将会导致死锁。
# 坏例子
@app.task
def update_page_info(url):
    page = fetch_page.delay(url).get()
    info = parse_page.delay(url, page).get()
    store_page_info.delay(url, info)

@app.task
def fetch_page(url):
    return myhttplib.get(url)

@app.task
def parse_page(url, page):
    return myparser.parse_document(page)

@app.task
def store_page_info(url, info):
    return PageInfo.objects.create(url, info)

# 好例子
def update_page_info(url):
    # fetch_page -> parse_page -> store_page
    # 将不同的任务签名链接起来创建一个任务链，三个子任务按顺序执行
    # 不建议同步执行子任务
    chain = fetch_page.s(url) | parse_page.s() | store_page_info.s(url)
    chain()

@app.task()
def fetch_page(url):
    return myhttplib.get(url)

@app.task()
def parse_page(page):
    return myparser.parse_document(page)

@app.task(ignore_result=True)
def store_page_info(info, url):
    PageInfo.objects.create(url=url, info=info)


# Django的模型对象不应该作为参数传递给任务
# Django 的模型对象。他们不应该作为参数传递给任务。几乎总是在任务运行时从数据库获取对象是最好的，因为老的数据会导致竞态条件
# 假象有这样一个场景，你有一篇文章，以及自动展开文章中缩写的任务:
class Article(models.Model):
    title = models.CharField()
    body = models.TextField()

@app.task
def expand_abbreviations(article):
    article.body.replace('MyCorp', 'My Corporation')
    article.save()
# 首先，作者创建一篇文章并保存，这时作者点击一个按钮初始化一个缩写展开任务
'''
>>> article = Article.objects.get(id=102)
>>> expand_abbreviations.delay(article)
'''
# 现在，队列非常忙，所以任务在2分钟内都不会运行。
# 与此同时，另一个作者修改了这篇文章，当这个任务最终运行，因为老版本的文章作为参数传递给了这个任务，所以这篇文章会回滚到老的版本。
# 修复这个竞态条件很简单，只要参数传递文章的 id 即可，此时可以在任务中重新获取这篇文
@app.task
def expand_abbreviations(article_id):
    article = Article.objects.get(id=article_id)
    article.body.replace('MyCorp', 'My Corporation')
    article.save()


# 使用on_commit函数处理事务
# 我们再看另外一个 celery 中处理事务的例子。
# 这是在数据库中创建一个文章对象的 Django 视图，此时传递主键给任务。
# 它使用 commit_on_success 装饰器，当视图返回时该事务会被提交，当视图抛出异常时会进行回滚。
from django.db import transaction
@transaction.commit_on_success
def create_article(request):
    article = Article.objects.create()
    expand_abbreviations.delay(article.pk)

# 如果在事务提交之前任务已经开始执行会产生一个竞态条件；数据库对象还不存在。
# 解决方案是使用 on_commit 回调函数来在所有事务提交成功后启动任务。
from django.db.transaction import on_commit
def create_article(request):
    article = Article.objects.create()
    on_commit(lambda: expand_abbreviations.delay(article.pk))


# 自定义重试延迟
# 当任务发送例外时，app.Task.retry() 函数可以用来重新执行任务。
# 当一个任务被重试，它在重试前会等待给定的时间，并且默认的由 default_retry_delay 属性定义。
# 默认设置为 3 分钟。注意延迟设置的单位是秒（int 或者 float）。你可以通过提供 countdown 参数覆盖这个默认值。
# retry in 30 minutes.
@app.task(bind=True, default_retry_delay=30 * 60)  
def add(self, x, y):
    try:
        something_raising()
    except Exception as exc:
        # overrides the default delay to retry after 1 minute
        raise self.retry(exc=exc, countdown=60)