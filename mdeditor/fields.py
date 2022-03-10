from __future__ import absolute_import

from django import forms
from django.db import models
from .widgets import MDEditorWidget


class MDTextFormField(forms.fields.CharField):
    """ 自定义表单字段 """
    def __init__(self, config_name='default', image_upload_folder='default', *args, **kwargs):
        kwargs.update({
            'widget': MDEditorWidget(config_name=config_name, image_upload_folder=image_upload_folder)
        })
        super(MDTextFormField, self).__init__(*args, **kwargs)


class MDTextField(models.TextField):
    """ 自定义模型字段 """

    def __init__(self, *args, **kwargs):
        self.config_name = kwargs.pop("config_name", "default")
        self.image_upload_folder = kwargs.pop("image_upload_folder", "default")
        super(MDTextField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {
            'form_class': MDTextFormField,
            'config_name': self.config_name,
            'image_upload_folder': self.image_upload_folder
        }
        defaults.update(kwargs)
        return super(MDTextField, self).formfield(**defaults)
