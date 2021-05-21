from django.urls import path, re_path
from . import views


app_name = 'app_comments'
urlpatterns = [
    path('article/<slug:article_slug>/postcomment', views.CommentPostView.as_view(), name='postcomment'),

    path('', views.CommentsView.as_view(), name='view'),
    # re_path(r'^(?P<content_obj>.+)/patch/$', views.CommentsView.as_view(), name='view'),

]