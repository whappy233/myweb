from celery import shared_task

"""
task方法参数
    name: 可以显式指定任务的名字; 默认是模块的命名空间中本函数的名字。
    serializer: 指定本任务的序列化的方法; 
    bind: 一个bool值, 设置是否绑定一个task的实例, 如果绑定, task实例会作为参数传递到任务方法中, 可以访问task实例的所有的属性, 即前面反序列化中那些属性
    base: 定义任务的基类, 可以以此来定义回调函数, 默认是Task类, 我们也可以定义自己的Task类
    default_retry_delay: 设置该任务重试的延迟时间, 当任务执行失败后, 会自动重试, 单位是秒, 默认3分钟; 
    autoretry_for: 设置在特定异常时重试任务, 默认False即不重试; 
    retry_backoff: 默认False, 设置重试时的延迟时间间隔策略; 
    retry_backoff_max: 设置最大延迟重试时间, 默认10分钟, 如果失败则不再重试; 
    retry_jitter: 默认True, 即引入抖动, 避免重试任务集中执行; 
"""

# from myweb import celery_app
# 当我们使用 @celery_app.task 装饰器定义我们的异步任务时, 那么这个任务依赖于根据项目名 myproject 生成的 Celery 实例
# 然而我们在进行 Django 开发时为了保证每个app的可重用性, 
# 我们经常会在每个 app 文件夹下编写异步任务, 这些任务并不依赖于具体的Django项目名。
# 使用 @shared_task 装饰器能让我们避免对某个项目名对应 Celery 实例的依赖, 使app的可移植性更强

# 当bind=True时, add函数第一个参数是self, 指的是task实例, 即views调用者的属性
@shared_task
def add(x, y):
    return x + y

@shared_task
def mul(x, y):
    return x * y

@shared_task
def xsum(numbers):
    return sum(numbers)
