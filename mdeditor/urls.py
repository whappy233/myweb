# -*- coding:utf-8 -*-

from django.urls import re_path as url_func

from .views import UploadView

urlpatterns = [
    url_func(r'^uploads/$', UploadView.as_view(), name='uploads'),
]
