from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


app_name = 'app_user'
urlpatterns = [
    path('login/', views.login, name='login'),                          # 登录
    path('register/', views.RegisterView.as_view(), name='register'),   # 注册
    # path('logout/', auth_views.LogoutView.as_view(next_page='app_blog:article_list'), name='logout'),  # 登出
    path('logout/', views.logout, name='logout'),  # 登出
    path('profile/', views.profile, name='profile'),                    # 资料编辑
    path('change_pw/', views.change_pw, name='change_pw'),              # 修改密码
    path('forget_pwd/', views.forget_pwd, name='forget_pwd'),           # 忘记密码
    path('check_code/', views.check_code, name='check_code'),           # 刷新验证码

    path('register_result/', views.register_result, name='register_result'),        # 注册成功以及邮箱验证

    path('send_email_vcode/', views.send_email_vcode, name='send_email_vcode'),     # ajax 发送邮件验证码
    path('profile/ajax/photo/', views.ajax_photo_upload, name='ajax_photo_upload'), # ajax 上传头像

    path('ajax_login/', views.ajax_login, name='ajax_login'), # ajax 登录
    path('ajax_register/', views.ajax_register, name='ajax_register'), # ajax 注册
]