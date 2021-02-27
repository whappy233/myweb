'Django多数据库配置'

# 当你刚刚开始建立一个网站时，可能每天只有数十到上百人访问。
# 这时你只有一个数据库，所有APP的数据表也都放一起的，一台普通的服务器能够应付, 也便于维护。
# 但是当访问量上来后，你会发现一台服务器和一个数据库会根本应付不了这个压力。
# 这时你可能希望实现数据库的主从配置，读写分离，把各个数据库放在不同的服务器上，
# 有的专门负责写入，有的专门负责读取，这时你就要学会使用Django同时连接多个数据库，并自定义读写操作。


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

    # 外键操作，判断两个对象之间是否是应该允许关系，是返回True,否则返回False，或者没有意见时返回 None 
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
        """
        决定是否允许迁移操作在别名为 db 的数据库上运行.
        如果可以返回True, 如果不可以返回 False ，或者没有意见时返回 None

        app_label 参数是要迁移的应用程序的标签。

        model_name 由大部分迁移操作设置来要迁移的模型的 model._meta.model_name （模型 __name__ 的小写版本） 的值。 
        对于 RunPython 和 RunSQL 操作的值是 None ，除非它们提示要提供它。

        hints 通过某些操作来向路由传达附加信息

        当设置 model_name ，hints 通常包含 'model' 下的模型类。
        注意它可能是 historical model ，因此没有任何自定义属性，方法或管理器。你应该只能依赖 _meta 。

        这个方法也可以用于确定给定数据库上模型的可用性。

        makemigrations 会在模型变动时创建迁移，但如果 allow_migrate() 返回 False ，
        任何针对 model_name 的迁移操作会在运行 migrate 的时候跳过。
        对于已经迁移过的模型，改变 allow_migrate() 的行为，可能会破坏主键，格外表或丢失的表。
        当 makemigrations 核实迁移历史，它跳过不允许迁移的 app 的数据库
        """
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
# article_object.save(using='db2', force_insert=True)
# force_insert 确保执行 SQL INSERT 操作
article_object.delete(using='db2')


# Django中使用多数据库注意事项:

# django 目前不为跨多个数据库的外键关系(ForeinKey)或多对多关系提供任何支持。
# 模型定义的任何外键和多对多关系字段都必须存在一个数据库内。


# 使用多个数据库管理器
User.objects.db_manager('new_users').create_user(...)

