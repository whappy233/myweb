'Django主从数据库配置'
'使用多数据库'


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




'使用多数据库'
# 使用多个数据库时最简单的方法是设置数据库路由方案，以保证对象对原始数据库的"粘性",默认所有的查询都会返回到default数据库中
# 在大型web项目中，我们常常会创建多个app来处理不同的业务，
# 如果希望实现app之间的数据库分离，
# 比如app01走数据库db1，app02走数据库db2，而不是实现读写分离。
# 我们可以定义如下所示的数据库路由, 然后将其加入settings.py 。

# settings.py
# test_django 为项目名, database_router 为路由文件名, DatabaseAppsRouter 为路由中创建的类名
DATABASE_ROUTERS = ['test_django.database_router.DatabaseAppsRouter']
DATABASE_APPS_MAPPING = {
    'app01':'db1',
    'app02':'db2',
}

# database_router.py
from django.conf import settings
DATABASE_MAPPING = settings.DATABASE_APPS_MAPPING   #在setting中定义的路由表
class DatabaseAppsRouter(object):
    # app_label: 位置参数是正在迁移的应用程序的标签
    # model_name: 多个迁移操作设置模型的值, 如:model._meta.app_label
    # 应用于读取类型对象的数据库模型，如果数据库提供附加信息会在hints字典中提供，最后如果没有则返回None
    def db_for_read(self, model, **hints):
        if model._meta.app_label in DATABASE_MAPPING:
            return DATABASE_MAPPING[model._meta.app_label]
        return None

    # 应用于写入类型对象的数据库模型，hints字典提供附加信息，如果没有则返回None
    def db_for_write(self, model, **hints):
        if model._meta.app_label in DATABASE_MAPPING:
            return DATABASE_MAPPING[model._meta.app_label]
        return None

    # 外键操作，判断两个对象之间是否是应该允许关系，是返回True,否则返回False，如果路由允许返回None
    def allow_relation(self, obj1, obj2, **hints):
        db_obj1 = DATABASE_MAPPING.get(obj1._meta.app_label)
        db_obj2 = DATABASE_MAPPING.get(obj2._meta.app_label)
        if db_obj1 and db_obj2:
            if db_obj1 == db_obj2:
                return True
            else:
                return False
        return None

    # db确定是否允许在具有别名的数据库上运行迁移操作，操作运行返回True，否则返回False，或者返回None，如果路由器没有意见
    def allow_syncdb(self, db, model):
        if db in DATABASE_MAPPING.values():
            return DATABASE_MAPPING.get(model._meta.app_label) == db
        elif model._meta.app_label in DATABASE_MAPPING:
            return False
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db in DATABASE_MAPPING.values():
            return DATABASE_MAPPING.get(app_label) == db
        elif app_label in DATABASE_MAPPING:
            return False
        return None

# app01/models.py
from django.db import models
class ap1(models.Model):
    username = models.CharField(max_length=30)
    class Meta:
        ...
        #app_label = 'app02'  # 如果指定将在 app02 对应的数据库下创建数据表

class ap2(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    birth_date = models.DateField()

# app02/models.py
from django.db import models
class ap3(models.Model):
    app2_name = models.CharField(max_length=50)
    sex = models.CharField(max_length=50)
    data = models.DateField()

class ap4(models.Model):
    app2 = models.CharField(max_length=50)
    sex1 = models.CharField(max_length=50)
    data1 = models.DateField()
    class Meta:
        db_table = 'mytable' # 自定义表名称


# 由于manage.py一次只能创建一个数据库，我们可以使用--database 选项来依次创建我们需要的数据库
# 如不指定会同步到default数据库上.
# 例如:
# python manage.py migrate   #同步默认数据库

# 将app01下models中的表创建到db01的数据库'db1'中
# python manage.py  migrate  --database=db1                                

# 将app02下models中的表创建到db02的数据库'db2'中
# python manage.py  migrate  --database=db2


# 在使用多数据库时，我们可以使用 using 方法来手动选择需要读写的数据库，如下所示:

Aricle.objects.using('db1').all()
article_object.save(using='db2')
 

# Django中使用多数据库注意事项:

# django 目前不为跨多个数据库的外键关系(ForeinKey)或多对多关系提供任何支持。
# 模型定义的任何外键和多对多关系字段都必须存在一个数据库内。