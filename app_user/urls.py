from django.urls import path, re_path
from app_user import views
from django.contrib.auth import views as auth_views


app_name = 'app_user'
urlpatterns = [
    path('login/', views.login, name='login'), # 登录
    path('logout/', auth_views.LogoutView.as_view(next_page='app_user:login'), name='logout'),  # 登出
    path('register/', views.RegisterView.as_view(), name='register'), # 注册
    path('change_pw/', views.change_pw, name='change_pw'),  # 修改密码
    path('forget_pwd/', views.forget_pwd, name='forget_pwd'), # 忘记密码
    path('send_email_vcode/', views.send_email_vcode, name='send_email_vcode'), # ajax 发送邮件验证码
    path('profile/', views.profile, name='profile'),  # 资料编辑
    path('check_code/', views.check_code, name='check_code'),  # 刷新验证码

    path('account/result.html', views.user_result, name='result'),

    path('profile/ajax/photo/', views.ajax_photo_upload, name='ajax_photo_upload'),  # ajax 上传头像

]