
from django.urls import include, path
from .views import FileView, FileUploads, xxxs
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'', FileView, basename='file')


app_name = 'app_common'
urlpatterns = [
    path('files/', include(router.urls)),
    path('FileUploads/', FileUploads),
    path('xxxs/', xxxs),

]