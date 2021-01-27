'''
Django 提供一个了 '信号分发器'机制，允许解耦的应用在框架的其它地方发生操作时会被通知到。 
通俗而讲Django信号的工作原理就是当某个事件发生的时候会发出一个信号(signals), 而监听这个信号的函数(receivers)就会立即执行。
Django信号的应用场景很多，尤其是用于不同模型或程序间的联动。
常见例子包括创建User对象实例时创建一对一关系的UserProfile对象实例，或者每当用户下订单时触发给管理员发邮件的动作.
'''


# 简单例子
# 假设我们有一个 User 模型，我们希望每次有 User 对象新创建时都打印出有新用户注册的提示信息，
# 我们可以使用 Django信号(signals）轻松实现。
# 我们的信号发送者 sender 是 User 模型，每当 User 模型执行 post_save 动作时就会发出信号。
# 此时我们自定义的 create_user 函数一旦监听到 User 发出的 post_save 信号就会执行，
# 先通过if created 判断对象是新创建的还是被更新的；如果对象是新创建的，就会打印出提示信息.
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(models.Model):
    name = models.CharField(max_length=16)
    gender = models.CharField(max_length=32, blank=True)

def create_user(sender, instance, created, **kwargs):
    if created:
        print("New user created!")
post_save.connect(create_user, sender=User)

# 在上例中我们使用了信号(post_save)自带的connect的方法将自定义的函数与信号发出者(sender)User模型进行了连接。
# 在实际应用中一个更常用的方式是使用 @receiver 装饰器实现发送者与监听函数的连接，如下所示。
# @receiver(post_save, sender=User) 读起来的意思就是监听 User 模型发出的 post_save 信号。
@receiver(post_save, sender=User)
def create_user(sender, instance, created, raw, using, update_fields, **kwargs):
    if created:
        print("New user created!")



# 例子:
# 利用Django信号实现不同模型的联动更新
# 我们有一个 Profile 模型，与User模型是一对一的关系。
# 我们希望创建 User 对象实例时也创建 Profile 对象实例，而使用 post_save 更新 User 对象时不创建新的 Profile 对象。
# 这时我们就可以自定义 create_user_profile 和 save_user_profile 两个监听函数，同时监听sender(User模型)发出的post_save信号。
# 由于post_save可同时用于模型的创建和更新，我们用if created这个判断来加以区别。

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birth_date = models.DateField(null=True, blank=True)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
   if created:
       Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

'Django常用内置信号'
# django.db.models.signals.pre_save & post_save     在模型调用 save()方法之前或之后发送。
# django.db.models.signals.pre_init& post_init      在模型调用_init_方法之前或之后发送。
# django.db.models.signals.pre_delete & post_delete 在模型调用delete()方法或查询集调用delete() 方法之前或之后发送。
# django.db.models.signals.m2m_changed              在模型多对多关系改变后发送。
# django.core.signals.request_started & request_finished Django     建立或关闭 HTTP 请求时发送。



'如何正确放置Django信号的监听函数代码'
# 在之前案例中，我们将Django信号的监听函数写在了models.py文件里。
# 当一个app的与信号相关的自定义监听函数很多时，此时models.py代码将变得非常臃肿。
# 一个更好的方式把所以自定义的信号监听函数集中放在app对应文件夹下的signals.py文件里，便于后期集中维护。

# 假如我们有个 app_user 的app，包含了User和Pofile模型，我们不仅需要在app_user文件夹下新建signals.py，
# 还需要修改 app_user 文件下apps.py和__init__.py，以导入创建的信号监听函数。

# app_user/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from app_user.models import User, Profile
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
  if created:
      Profile.objects.create(user=instance)
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

# app_user/apps.py
from django.apps import AppConfig
class AppUserConfig(AppConfig):
    name = 'app_user'

    def ready(self):
        import app_user.signals

# app_user/__init__.py
default_app_config = 'app_user.apps.AppUserConfig'
