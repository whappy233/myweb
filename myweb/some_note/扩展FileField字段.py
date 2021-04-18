
# Django模型中自带的ImageField和FileField字段并不会也不能限制用户上传的图片或文件的格式和大小，这给Web APP开发带来了很大的安全隐患。
# 当然你可以通过自定义form类中的clean的方法来添加对image或file字段进行验证，从而限制上传文件格式和大小，然而这并不是最佳处理方法，
# 因为这意味者每次你的模型里包含了图片或文件字段，你都要自定义forms类，并添加clean方法，从而造成大量代码重复。
# 一个处理该问题的最佳方式是扩展Django的FileFiled字段，在创建模型时直接设置可以接受的文件类型，并限定可以上传的文件的最大尺寸。
# 本文教你如何扩展Django的FileField字段，并展示如何在模型中使用它，从而以最佳方式限制用户上传文件的格式与大小

from django.db.models import FileField
from django.forms import forms
from django.template.defaultfilters import filesizeformat


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
from django.db import models

class File(models.Model):
    file = RestrictedFileField(upload_to=user_directory_path, max_length=100,
            max_upload_size=5242880,
            content_types=['application/pdf', 
                            'application/excel', 
                            'application/msword',
                            'text/plain', 
                            'text/csv', 
                            'application/zip'])


class Image(models.Model):
    file = RestrictedFileField(upload_to=user_directory_path, max_length=100,
            max_upload_size=5242880,
            content_types=[
                'image/jpeg', 
                'image/gif', 
                'image/gif', 
                'image/bmp', 
                'image/tiff'])