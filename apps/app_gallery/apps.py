
from django.apps import AppConfig
from django.core.serializers.python import Serializer as Builtin_Serializer
from django.db import models
from django.utils.encoding import is_protected_type, smart_text

class AppGalleryConfig(AppConfig):
    name = 'app_gallery'
    verbose_name = '相册'



class Serializer(Builtin_Serializer):
    '''
    {
        "pk":1,
        "model":"events.phone",
        "alt": 'xxx', 
        "thumb": 'xxx', 
        "image": 'xxx', 
        "created_time": 'xxx'
    }
    '''

    def _value_from_field(self, obj, field):
        '''在给定的模型实例中返回此字段的值'''

        value = field.value_from_object(obj)

        # 对于 ImageField 返回url
        if isinstance(field, models.ImageField):
            if value:
                return value.url
            else:
                return ''

        # 受保护的类型（例如，无，数字，日期和小数之类的基元）按原样传递。
        # 所有其他值都将首先转换为字符串。
        if is_protected_type(value):
            return value
        return  field.value_to_string(obj)

    def get_dump_object(self, obj):
        if self.selected_fields:
            if 'pk' in self.selected_fields:
                self._current['pk'] = smart_text(obj._get_pk_val(), strings_only=True)
            if 'id' in self.selected_fields:
                self._current['id'] = smart_text(obj._get_pk_val(), strings_only=True)
        # self._current['model'] = smart_text(obj._meta)
        return self._current

from django.core.serializers import BUILTIN_SERIALIZERS
BUILTIN_SERIALIZERS['json'] = 'app_gallery.apps'


