'''
支持动态指定字段的序列化器

1. 接口默认可以取到 Serializer.Meta.fields里所有的字段.
2. 查询接口 (detail, list)  可以传参 fields动态指定需要序列化返回的字段.
3. 更新接口 (update) 可以传参fields动态指定允许反序列化保存的字段.
4. 可以在 Serializer.Meta 中配置 list_fields 属性, list 接口用这个属性作为序列化字段, 
    没配这个属性用原来的Meta.fields序列化;(如果同时传参fields进来做序列化, 优先传参指定的fields).
'''

from rest_framework import serializers


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """支持动态指定字段的序列化器, 传参fields, 序列化和反序列化都支持"""
    Meta: type

    def __init__(self, *args, **kwargs):
        """
        支持字段动态生成的序列化器, 从默认的 Meta.fields 中过滤, 无关字段不查不序列化
        """
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        if fields is not None:
            allow = set(fields)
            existing = set(self.fields)
            for f in existing - allow:
                self.fields.pop(f)

    def __new__(cls, *args, **kwargs):
        """
        __new__ 方法在设置了 `many=True` 时自动创建 `ListSerializer` 类.
        list序列化时, 首先使用传参的fields, 默认用 meta.list_fields 作为序列化字段
        """

        if kwargs.pop('many', False):
            fields = getattr(cls.Meta, 'list_fields', None)
            if fields and 'fields' not in kwargs:
                kwargs['fields'] = fields
            return cls.many_init(*args, **kwargs)
        return super().__new__(cls, *args, **kwargs)
