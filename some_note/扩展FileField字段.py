
# Django模型中自带的ImageField和FileField字段并不会也不能限制用户上传的图片或文件的格式和大小，这给Web APP开发带来了很大的安全隐患。
# 当然你可以通过自定义form类中的clean的方法来添加对image或file字段进行验证，从而限制上传文件格式和大小，然而这并不是最佳处理方法，
# 因为这意味者每次你的模型里包含了图片或文件字段，你都要自定义forms类，并添加clean方法，从而造成大量代码重复。
# 一个处理该问题的最佳方式是扩展Django的FileFiled字段，在创建模型时直接设置可以接受的文件类型，并限定可以上传的文件的最大尺寸。
# 本文教你如何扩展Django的FileField字段，并展示如何在模型中使用它，从而以最佳方式限制用户上传文件的格式与大小

import re
from django.db import models
from django.conf import Settings
from django.db.models import FileField, Q, SlugField, UniqueConstraint
from django.db.models.constants import LOOKUP_SEP
from django.forms import forms
from django.template.defaultfilters import filesizeformat, slugify
from django.utils.encoding import force_str



class RestrictedFileField(FileField):
    """ max_upload_size:
        2.5MB - 2621440
        5MB - 5242880
        10MB - 10485760
        20MB - 20971520
        50MB - 5242880
        100MB 104857600
        250MB - 214958080
        500MB - 429916160
    """
    def __init__(self, *args, **kwargs):
        self.content_types = kwargs.pop("content_types", [])
        self.max_upload_size = kwargs.pop("max_upload_size", [])
        super().__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super().clean(*args, **kwargs)
        file = data.file

        try:
            content_type = file.content_type
            if content_type in self.content_types:
                if file.size > self.max_upload_size:
                    raise forms.ValidationError('Please keep filesize under {}. Current filesize {}'
                            .format(filesizeformat(self.max_upload_size), filesizeformat(file.size)))
            else:
                raise forms.ValidationError('This file type is not allowed.')
        except AttributeError:
            pass
        return data

# usage:
class File(models.Model):
    file = RestrictedFileField(upload_to='image/%Y/%d', max_length=100,
            max_upload_size=5242880,
            content_types=['application/pdf', 
                            'application/excel', 
                            'application/msword',
                            'text/plain', 
                            'text/csv', 
                            'application/zip'])

class Image(models.Model):
    file = RestrictedFileField(upload_to='image/%Y/%d', max_length=100,
            max_upload_size=5242880,
            content_types=[
                'image/jpeg', 
                'image/gif', 
                'image/gif', 
                'image/bmp', 
                'image/tiff'])



# 最大唯一查询尝试
MAX_UNIQUE_QUERY_ATTEMPTS = getattr(Settings, 'EXTENSIONS_MAX_UNIQUE_QUERY_ATTEMPTS', 100)


class UniqueFieldMixin:

    def check_is_bool(self, attrname):
        if not isinstance(getattr(self, attrname), bool):
            raise ValueError("'{}' argument must be True or False".format(attrname))

    @staticmethod
    def _get_fields(model_cls):
        return [
            (f, f.model if f.model != model_cls else None) for f in model_cls._meta.get_fields()
            if not f.is_relation or f.one_to_one or (f.many_to_one and f.related_model)
        ]

    def get_queryset(self, model_cls, slug_field):
        for field, model in self._get_fields(model_cls):
            if model and field == slug_field:
                return model._default_manager.all()
        return model_cls._default_manager.all()

    def find_unique(self, model_instance, field, iterator, *args):
        # exclude the current model instance from the queryset used in finding
        # next valid hash
        queryset = self.get_queryset(model_instance.__class__, field)
        if model_instance.pk:
            queryset = queryset.exclude(pk=model_instance.pk)

        # form a kwarg dict used to implement any unique_together constraints
        kwargs = {}
        for params in model_instance._meta.unique_together:
            if self.attname in params:
                for param in params:
                    kwargs[param] = getattr(model_instance, param, None)

        # for support django 2.2+
        query = Q()
        constraints = getattr(model_instance._meta, 'constraints', None)
        if constraints:
            unique_constraints = filter(
                lambda c: isinstance(c, UniqueConstraint), constraints
            )
            for unique_constraint in unique_constraints:
                if self.attname in unique_constraint.fields:
                    condition = {
                        field: getattr(model_instance, field, None)
                        for field in unique_constraint.fields
                        if field != self.attname
                    }
                    query &= Q(**condition)

        new = next(iterator)
        kwargs[self.attname] = new
        while not new or queryset.filter(query, **kwargs):
            new = next(iterator)
            kwargs[self.attname] = new
        setattr(model_instance, self.attname, new)
        return new


class AutoSlugField(UniqueFieldMixin, SlugField):
    """
    AutoSlugField

    By default, sets editable=False, blank=True.

    Required arguments:

    populate_from
        Specifies which field, list of fields, or model method
        the slug will be populated from.

        populate_from can traverse a ForeignKey relationship
        by using Django ORM syntax:
            populate_from = 'related_model__field'

    Optional arguments:

    separator
        Defines the used separator (default: '-')

    overwrite
        If set to True, overwrites the slug on every save (default: False)

    slugify_function
        Defines the function which will be used to "slugify" a content
        (default: :py:func:`~django.template.defaultfilters.slugify` )

    It is possible to provide custom "slugify" function with
    the ``slugify_function`` function in a model class.

    ``slugify_function`` function in a model class takes priority over
    ``slugify_function`` given as an argument to :py:class:`~AutoSlugField`.

    Example

    .. code-block:: python

        # models.py

        from django.db import models

        from django_extensions.db.fields import AutoSlugField


        class MyModel(models.Model):
            def slugify_function(self, content):
                return content.replace('_', '-').lower()

            title = models.CharField(max_length=42)
            slug = AutoSlugField(populate_from='title')

    Inspired by SmileyChris' Unique Slugify snippet:
    http://www.djangosnippets.org/snippets/690/
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('blank', True)
        kwargs.setdefault('editable', False)

        populate_from = kwargs.pop('populate_from', None)
        if populate_from is None:
            raise ValueError("missing 'populate_from' argument")
        else:
            self._populate_from = populate_from

        if not callable(populate_from):
            if not isinstance(populate_from, (list, tuple)):
                populate_from = (populate_from, )

            if not all(isinstance(e, str) for e in populate_from):
                raise TypeError("'populate_from' must be str or list[str] or tuple[str], found `%s`" % populate_from)

        self.slugify_function = kwargs.pop('slugify_function', slugify)
        self.separator = kwargs.pop('separator', '-')
        self.overwrite = kwargs.pop('overwrite', False)
        self.check_is_bool('overwrite')
        self.overwrite_on_add = kwargs.pop('overwrite_on_add', True)
        self.check_is_bool('overwrite_on_add')
        self.allow_duplicates = kwargs.pop('allow_duplicates', False)
        self.check_is_bool('allow_duplicates')
        self.max_unique_query_attempts = kwargs.pop('max_unique_query_attempts', MAX_UNIQUE_QUERY_ATTEMPTS)
        super().__init__(*args, **kwargs)

    def _slug_strip(self, value):
        """
        Clean up a slug by removing slug separator characters that occur at
        the beginning or end of a slug.

        If an alternate separator is used, it will also replace any instances
        of the default '-' separator with the new separator.
        """
        re_sep = '(?:-|%s)' % re.escape(self.separator)
        value = re.sub('%s+' % re_sep, self.separator, value)
        return re.sub(r'^%s+|%s+$' % (re_sep, re_sep), '', value)

    @staticmethod
    def slugify_func(content, slugify_function):
        if content:
            return slugify_function(content)
        return ''

    def slug_generator(self, original_slug, start):
        yield original_slug
        for i in range(start, self.max_unique_query_attempts):
            slug = original_slug
            end = '%s%s' % (self.separator, i)
            end_len = len(end)
            if self.slug_len and len(slug) + end_len > self.slug_len:
                slug = slug[:self.slug_len - end_len]
                slug = self._slug_strip(slug)
            slug = '%s%s' % (slug, end)
            yield slug
        raise RuntimeError('max slug attempts for %s exceeded (%s)' % (original_slug, self.max_unique_query_attempts))

    def create_slug(self, model_instance, add):
        slug = getattr(model_instance, self.attname)
        use_existing_slug = False
        if slug and not self.overwrite:
            # Existing slug and not configured to overwrite - Short-circuit
            # here to prevent slug generation when not required.
            use_existing_slug = True

        if self.overwrite_on_add and add:
            use_existing_slug = False

        if use_existing_slug:
            return slug

        # get fields to populate from and slug field to set
        populate_from = self._populate_from
        if not isinstance(populate_from, (list, tuple)):
            populate_from = (populate_from, )

        slug_field = model_instance._meta.get_field(self.attname)
        slugify_function = getattr(model_instance, 'slugify_function', self.slugify_function)

        # slugify the original field content and set next step to 2
        slug_for_field = lambda lookup_value: self.slugify_func(
            self.get_slug_fields(model_instance, lookup_value),
            slugify_function=slugify_function
        )
        slug = self.separator.join(map(slug_for_field, populate_from))
        start = 2

        # strip slug depending on max_length attribute of the slug field
        # and clean-up
        self.slug_len = slug_field.max_length
        if self.slug_len:
            slug = slug[:self.slug_len]
        slug = self._slug_strip(slug)
        original_slug = slug

        if self.allow_duplicates:
            setattr(model_instance, self.attname, slug)
            return slug

        return self.find_unique(
            model_instance, slug_field, self.slug_generator(original_slug, start))

    def get_slug_fields(self, model_instance, lookup_value):
        if callable(lookup_value):
            # A function has been provided
            return "%s" % lookup_value(model_instance)

        lookup_value_path = lookup_value.split(LOOKUP_SEP)
        attr = model_instance
        for elem in lookup_value_path:
            try:
                attr = getattr(attr, elem)
            except AttributeError:
                raise AttributeError(
                    "value {} in AutoSlugField's 'populate_from' argument {} returned an error - {} has no attribute {}".format(
                        elem, lookup_value, attr, elem))

        if callable(attr):
            return "%s" % attr()

        return attr

    def pre_save(self, model_instance, add):
        value = force_str(self.create_slug(model_instance, add))
        return value

    def get_internal_type(self):
        return "SlugField"

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs['populate_from'] = self._populate_from
        if not self.separator == '-':
            kwargs['separator'] = self.separator
        if self.overwrite is not False:
            kwargs['overwrite'] = True
        if self.allow_duplicates is not False:
            kwargs['allow_duplicates'] = True
        return name, path, args, kwargs


