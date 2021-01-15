from django.urls import path, include
from app_sheet import views




app_name = 'app_sheet'
urlpatterns = [
    path('', views.index, name='index'),
    path('update/', views.update, name='update'),
]
