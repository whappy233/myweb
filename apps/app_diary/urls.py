
from django.urls import path
from . import views



app_name = 'app_diary'
urlpatterns = [
    path('', views.DiaryList.as_view(), name='index'),
]
