'Django主从数据库配置'
'Django项目按APP分库'


# 当你刚刚开始建立一个网站时，可能每天只有数十到上百人访问。
# 这时你只有一个数据库，所有APP的数据表也都放一起的，一台普通的服务器能够应付, 也便于维护。
# 但是当访问量上来后，你会发现一台服务器和一个数据库会根本应付不了这个压力。
# 这时你可能希望实现数据库的主从配置，读写分离，把各个数据库放在不同的服务器上，
# 有的专门负责写入，有的专门负责读取，这时你就要学会使用Django同时连接多个数据库，并自定义读写操作。



'第一步 修改项目的 settings 配置 '
# 在 settings.py 中配置需要连接的多个数据库名称和登录信息。
# 在下例中我们自定义了3个数据库，1个主数据库(primary), 2个从数据库(replica)。
#project/settings.py
DATABASES = {
    'default': {},
    'primary': {
        'NAME': 'primary',
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'xxxx',
        'PORT': 'xxxx',
        'USER': 'mysql_user',
        'PASSWORD': 'spam',
    },
    'replica1': {
        'NAME': 'replica1',
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'xxxx',
        'PORT': 'xxxx',
        'USER': 'mysql_user',
        'PASSWORD': 'eggs',
    },
    'replica2': {
        'NAME': 'replica2',
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'xxxx',
        'PORT': 'xxxx',
        'USER': 'mysql_user',
        'PASSWORD': 'bacon',
    },
}
# 我们还需要在 settings.py 添加我们手动编写的数据库路由Router。
# 路由的作用是为数据库的读写制定规则。
DATABASE_ROUTERS = ['Project.database_router.PrimaryReplicaRouter']
# 注意: 主从数据库的同步是通过MySQL配置实现的，而不是Django实现的。
# Django只负责多个数据库的访问，不负责各个数据库的同步工作。如果你定义了多个路由，请一定注意路由的执行顺序。



'第二步 自定义数据库路由Router'
# 在Django项目的根目录下创建 database_router.py 文件, 添加如下代码，自定义数据库路由。
# 该路由规定了读取数据时将随机从replica1和replica2数据库中读取，而写入数据总是写入主数据库primary。
# 该路由还允许三个数据库中的字段建立联系。
import random
class PrimaryReplicaRouter(object):
    def db_for_read(self, model, **hints):
        """
        Reads go to a randomly-chosen replica.

        建议 model 对象进行读操作时使用的数据库。
        如果一个数据库操作可以提供对选择数据库有用的附加信息，那么可以通过 hints 字典提供。
        如果没有建议则返回 None
        """
        return random.choice(['replica1', 'replica2'])
 
    def db_for_write(self, model, **hints):
        """
        Writes always go to primary.

        建议 model 对象进行写操作时使用的数据库。
        如果一个数据库操作可以提供对选择数据库有用的附加信息，那么可以通过 hints 字典提供。
        如果没有建议则返回 None
        """
        return 'primary'
 
    def allow_relation(self, obj1, obj2, **hints):
        """
        Relations between objects are allowed if both objects are
        in the primary/replica pool.

        当 obj1 和 obj2 之间允许有关系时返回 True ，不允许时返回 False ，或者没有意见时返回 None 。
        这是一个纯粹的验证操作，用于外键和多对多操作中，两个对象的关系是否被允许
        """
        db_list = ('primary', 'replica1', 'replica2')
        if obj1._state.db in db_list and obj2._state.db in db_list:
            return True
        return None
 
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        All models end up in this pool.

        决定 model 是否可以和 db 为别名的数据库同步。
        如果可以返回True ， 如果不可以返回 False ，或者没有意见时返回 None 
        """
        return True






'Django项目按APP分库'
# 在大型web项目中，我们常常会创建多个app来处理不同的业务，
# 如果希望实现app之间的数据库分离，
# 比如app01走数据库db1，app02走数据库db2，而不是实现读写分离。
# 我们可以定义如下所示的数据库路由, 然后将其加入settings.py 。

class AppDBRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'app01':
            return 'db1'
        if model._meta.app_label == 'app02':
            return 'db2'

    def db_for_write(self, model, **hints):
       if model._meta.app_label == 'app01':
            return 'db1'
       if model._meta.app_label == 'app02':
            return 'db2'


# 由于manage.py一次只能创建一个数据库，我们可以使用--database选项来依次创建我们需要的数据库。例如:

# 将app01下models中的表创建到db01的数据库'db1'中
# python manage.py  migrate  --database=db1                                

# 将app02下models中的表创建到db02的数据库'db2'中
# python manage.py  migrate  --database=db2

# 在使用多数据库时，我们可以使用 using 方法来手动选择需要读写的数据库，如下所示:

Aricle.objects.using('db1').all()
post_object.save(using='db2')
 

# Django中使用多数据库注意事项:

# django 目前不为跨多个数据库的外键关系(ForeinKey)或多对多关系提供任何支持。
# 模型定义的任何外键和多对多关系字段都必须存在一个数据库内。