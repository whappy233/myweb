

# 字段注释
# 利用Field定义中help_text属性作为注释。
# 修改django/db/backends/base/schema.py 文件，column_sql函数，如下：
from django.db.backends.base.schema import BaseDatabaseSchemaEditor


...

def column_sql(self, model, field, include_default=False):
    """
    Takes a field and returns its column definition.
    The field must already have had set_attributes_from_name called.
    """
    ...

    # Optionally add the tablespace if it's an implicitly indexed column
    tablespace = field.db_tablespace or model._meta.db_tablespace
    if tablespace and self.connection.features.supports_tablespaces and field.unique:
        sql += " %s" % self.connection.ops.tablespace_sql(tablespace, inline=True)

    # 增加针对mysql注释的处理
    if self.connection.client.executable_name == 'mysql' and field.help_text:
        sql += " COMMENT '%s'" % field.help_text

    # Return the sql
    return sql, params


