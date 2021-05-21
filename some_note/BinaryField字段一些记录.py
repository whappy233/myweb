# 当同时存在BinaryField类型字段和排序条件时，mysql的性能会非常差.

# 解决办法

'''
---------------------------------------------------------------------------------
1、针对分页器的优化 
    思路：ORM具有惰性，在ORM转成sql真正去数据库查询前进行拦截，获取并修改sql，去掉无关字段再执行sql。
    自定义分页器，重写count方法：
'''
#   1、新建paginator.py文件：
from django.core.paginator import Paginator
from django.utils.functional import cached_property
from ORM_performance import ORM

class HRMSPaginator(Paginator):

    @cached_property
    def count(self):
        """
        返回所有页面上的对象总数

        原始的django分页器进行总数量查询时，ORM转SQL时会产生一个包含所有字段的子查询臃肿语句，
        并且BinaryField类型的字段会对SQL性能造成非常巨大影响.
        """
        try:
            # object_list 是初始化分页器传进来的 queryset
            return ORM.count(self.object_list)
        except (AttributeError, TypeError):
            return len(self.object_list)

#   2、新建 ORM_performance.py 文件：
from django.db import connection
class ORM:
    _bloated_field = ["`hr_hruser`.`cv_data`", "`hr_interview`.`cv_safe_data`", "`hr_interview`.`evaluation_1_data`",
                      "`hr_interview`.`evaluation_2_data`", "`hr_interview`.`evaluation_3_data`",
                      "`hr_interview`.`offer_data`"
                      ] #这些字段都是BinaryField类型
    @classmethod
    def count(cls, queryset):
        """接收一个查询集并返回查询集的长度"""
        cursor = connection.cursor()
        sql = queryset.query.__str__()
        # 去掉无关字段
        for field in cls._bloated_field:
            if field in sql:
                sql = sql.replace(field, "")
        new_sql = sql.replace(", ,", ",")
        try:
            # new_sql 中当包含以字符串为参数的查询时，execute会报错，因为new_sql中的字符串并没有被引号引起来。
            # 而sql语句要求字符串必须要有引号的
            return cursor.execute(new_sql)
        except:
            try:
                return queryset.count()
            except (AttributeError, TypeError):
                return len(queryset)
        finally:
            cursor.close()


#   3、修改\xadmin\views\list.py
class ListAdminView(ModelAdminView):
    """
    Display models objects view. this class has ordering and simple filter features.
    """
    list_display = ('__str__',)
    list_display_links = ()
    list_display_links_details = False
    list_select_related = None
    list_per_page = 50
    list_max_show_all = 200
    list_exclude = ()
    search_fields = ()
    paginator_class = HRMSPaginator   # 修改一：使用自定义paginator
    ordering = None

    def make_result_list(self):
        # Get search parameters from the query string.
        self.list_queryset = self.get_list_queryset()
        self.ordering_field_columns = self.get_ordering_field_columns()
        self.paginator = self.get_paginator()

        # Get the number of objects, with admin filters applied.
        self.result_count = self.paginator.count

        self.can_show_all = self.result_count <= self.list_max_show_all
        self.multi_page = self.result_count > self.list_per_page

        # Get the list of objects to display on this page.
        if (self.show_all and self.can_show_all) or not self.multi_page:
            self.result_list = self.list_queryset._clone()
        else:
            try:
                self.result_list = self.paginator.page(
                    self.page_num + 1).object_list
            except InvalidPage:
                if ERROR_FLAG in self.request.GET.keys():
                    return SimpleTemplateResponse('xadmin/views/invalid_setup.html', {
                        'title': _('Database error'),
                    })
                return HttpResponseRedirect(self.request.path + '?' + ERROR_FLAG + '=1')
        self.has_more = self.result_count > (
            self.list_per_page * self.page_num + ORM.count(self.result_list)) # 修改二：使用自定义方法查询queryset长度



'''
---------------------------------------------------------------------------------
2、针对数据渲染的优化
如果排序需求不是很大，可以先去掉排序。

也可考虑将cv_data这样的字段单独存储到一张表，以外键关联，专门存储二进制或其他较大的文本数据
'''


'''
结论
1、数据库最好不用存放大文件，严格说不要使用 BinaryField 类型字段，如果必须，那就用单独一张表保存，以外键与业务表关联。

2、User.objects.all()、User.objects.filter()、User.objects.get()等类似的ORM转化成SQL时，
通常都会产生一个类似 `select field1, field2...所有字段 from .. where .. ` 这样的臃肿语句，即使你仅仅只想查找一个字段。
所以尽量使用 User.objects.values()、User.objects.values_list() 来避免以上问题。
并且包含BinaryField类型的字段时，会对SQL性能造成非常巨大影响。

3、`select * form hr_hruser order by id limit 0,20` 这样的语句执行顺序为先取出表中所有数据，然后进行排序，最后拿到前20条。
如果数据量非常大，那排序将是非常耗时的。
当select username， cv_data .. form hr_hruser order by id limit 0,20 这样的语句同时存在BinaryField和排序时，即使数据量很小，查询也会非常耗时。
去掉任意一个条件（BinaryField或者order by）即可改善
'''