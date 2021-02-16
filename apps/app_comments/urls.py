from django.urls import path
from app_comments import views


app_name = 'app_comments'
urlpatterns = [
    path('article/<int:article_id>/postcomment', views.CommentPostView.as_view(), name='postcomment'),
    path('ajax_delete_comment/', views.ajax_delete_comment, name='ajax_delete_comment')
]