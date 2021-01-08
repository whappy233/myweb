from django.urls import path, re_path
from app_user import views
from django.contrib.auth import views as auth_views


app_name = 'app_user'
urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='app_user:login'), name='logout'),  # 登出
    path('register/', views.register, name='register'),  #注册
    path('change_pw/', views.change_pw, name='change_pw'),  # 修改密码
    path('forget_pwd/', views.forget_pwd, name='forget_pwd'), # 忘记密码
    path('send_email_vcode/', views.send_email_vcode, name='send_email_vcode'), # 忘记密码发送邮件验证码
    path('profile/', views.profile, name='profile'),
    path('check_code/', views.check_code, name='check_code'),

    path('profile/ajax/photo/', views.ajax_photo_upload, name='ajax_photo_upload'),

]