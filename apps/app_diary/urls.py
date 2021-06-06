
from django.urls import path
from . import views



app_name = 'app_diary'
urlpatterns = [
    path('', views.DiaryList.as_view(), name='index'),
    path('details/<slug:slug>/', views.details, name='diary_detail'),  # 文章详情

]
