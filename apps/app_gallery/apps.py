from django.apps import AppConfig


class AppGalleryConfig(AppConfig):
    name = 'app_gallery'
    verbose_name = '相册'




import datetime
import decimal
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.base import ModelBase
from django.utils.encoding import smart_text
from django.core.serializers.json import Serializer as Builtin_Serializer

class Serializer(Builtin_Serializer):
    # {
    #     "pk":1,
    #     "model":"events.phone",
    #     "alt": 'xxx', 
    #     "thumb": 'xxx', 
    #     "image": 'xxx', 
    #     "create_date": 'xxx'
    # }

    def _init_options(self):
        self._current = None
        self.json_kwargs = self.options.copy()
        self.json_kwargs.pop('stream', None)
        self.json_kwargs.pop('fields', None)
        if self.options.get('indent'):
            # Prevent trailing spaces
            self.json_kwargs['separators'] = (',', ': ')
        self.json_kwargs.setdefault('cls', JSONEncoder)


    def get_dump_object(self, obj):
        # self._current['id'] = smart_text(obj._get_pk_val(), strings_only=True)
        # self._current['model'] = smart_text(obj._meta)
        return self._current

from django.core.serializers import BUILTIN_SERIALIZERS
BUILTIN_SERIALIZERS['json'] = 'app_gallery.apps'


class JSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.strftime('%Y年%m月%d日 %H:%M:%S')
        elif isinstance(o, datetime.date):
            return o.strftime('%Y-%m-%d')
        elif isinstance(o, decimal.Decimal):
            return str(o)
        elif isinstance(o, ModelBase):
            return '%s.%s' % (o._meta.app_label, o._meta.model_name)
        else:
            try:
                return super(JSONEncoder, self).default(o)
            except Exception:
                return smart_text(o)

