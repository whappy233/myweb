import io
from django.contrib import auth
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse


from .forms import (EditForm, LoginForm, ProfileEditForm, PwdChangeForm,
                    RegistrationForm, UserEditForm, UserPhotoUploadForm)
from .models import UserProfile
from .utils import create_validate_code as CheckCode, crop_image


class CustomBackend(ModelBackend):
    """
    实现用户名邮箱手机号登录
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 不希望用户存在两个，get只能有一个。两个是get失败的一种原因 Q为使用并集查询
            user = User.objects.get(Q(username=username) | Q(
                email=username) | Q(profile__telephone=username))
            # UserProfile继承的AbstractUser中有def check_password(self, raw_password):
            if user.check_password(password):
                return user
        except Exception as e:
            return None

# 返回验证码图片
def check_code(request):
    try:
        stream = io.BytesIO()
        # img图片对象, code在图像中写的内容
        img, code = CheckCode()
        img.save(stream, "png")
        # 图片页面中显示,立即把session中的CheckCode更改为目前的随机字符串值
        request.session["CheckCode"] = code
        return HttpResponse(stream.getvalue())
    except Exception as e:
        return HttpResponse("请求异常：{}".format(repr(e)))


def register(request):
    message = ''
    if request.method == 'POST':

        form = RegistrationForm(request.POST)
        checkcode = request.POST.get("check_code")
        if checkcode.lower() != request.session['CheckCode'].lower():  # 验证验证码
            message = "验证码错误"

        elif form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password2']
            # 使用内置User自带create_user方法创建用户，不需要使用save()
            user = User.objects.create_user(username=username, password=password, email=email)
            # 在创建User时同时创建与之关联的UserProfile对象
            user_profile = UserProfile(user=user)
            # 如果直接使用objects.create()方法后不需要使用save()
            user_profile.save()
            return redirect("app_user:login")
    else:
        form = RegistrationForm()
    return render(request, 'app_user/registration.html', {'form': form, 'message': message})

def login(request):
    # 第三步
    # from .tasks import XXX
    # r = XXX.delay()  # 添加到Celery, 可通过 r.result获取结果
    # print(dir(r))
    # r.ready()     # 查看任务状态，返回布尔值,  任务执行完成, 返回 True, 否则返回 False.
    # r.wait()      # 会阻塞等待任务完成, 返回任务执行结果，很少使用；
    # r.get(timeout=1)       # 获取任务执行结果，可以设置等待时间，如果超时但任务未完成返回None；
    # r.result      # 任务执行结果，未完成返回None；
    # r.state       # PENDING, START, SUCCESS，任务当前的状态
    # r.status      # PENDING, START, SUCCESS，任务当前的状态
    # r.successful  # 任务成功返回true
    # r.traceback  # 如果任务抛出了一个异常，可以获取原始的回溯信息

    next = request.GET.get('next', reverse('app_blog:post_list'))

    message = ''
    if request.method == 'POST':

        form = LoginForm(request.POST)
        checkcode = request.POST.get("check_code")
        # if checkcode.lower() != request.session['CheckCode'].lower():  # 验证验证码
        #     message = "验证码错误"

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = auth.authenticate(username=username, password=password)
            if user and user.is_active:
                auth.login(request, user)
                return redirect(next)


            else:
                message = '密码错误。请重试。'
    else:
        form = LoginForm()
    return render(request, 'app_user/login.html', {'form': form, 'message': message})

@login_required
def change_pw(request):
    message = ''
    if request.method == 'POST':
        form = PwdChangeForm(request.POST)

        checkcode = request.POST.get("check_code")
        if checkcode.lower() != request.session['CheckCode'].lower():  # 验证验证码
            message = "验证码错误"

        elif form.is_valid():
            old_pw = form.cleaned_data['old_pw']
            pw1 = form.cleaned_data['pw1']
            username = request.user.username       # 获取当前登录用户的用户名
            user = auth.authenticate(username=username, password=old_pw)
            if user:
                user.set_password(pw1)
                user.save()
                return redirect('app_blog:post_list')
            else:
                message = '密码错误。请重试。'
    else:
        form = PwdChangeForm(initial={'username': request.user.username})

    return render(request, 'app_user/change_pw.html', {'form': form, 'message': message})


@login_required
def profile(request):
    message = ''
    if request.method == 'POST':
        user_form = UserEditForm(data=request.POST, instance=request.user)
        profile_form = ProfileEditForm(data=request.POST, files=request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            message = '信息修改成功'
        else:
            message = '修改失败'

    user_form = UserEditForm(instance=request.user)  # 初始化表单
    profile_form = ProfileEditForm(instance=request.user.profile)
    # profile_form = EditForm()
    return render(request,
                  'app_user/profile.html',
                  context={
                      'user_form': user_form,
                      'profile_form': profile_form,
                      'message': message})


@login_required
def ajax_photo_upload(request):
    user = request.user
    user_profile = get_object_or_404(UserProfile, user=user)

    if request.method == "POST":
        form = UserPhotoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            photo = request.FILES['photo_file']  # 获取上传图片
            data = request.POST['photo_data']  # 获取ajax返回图片坐标

            if photo.size/1024 > 3000:
                return JsonResponse({"message": "图片大小请控制在3M以内, 请重新上传。", })

            old_photo = user_profile.photo  # 旧的头像
            cropped_photo = crop_image(old_photo, photo, data, user.id)  # 裁剪头像
            user_profile.photo = cropped_photo  # 将图片路径修改到当前用户数据库
            user_profile.save()

            # 向前台返回一个json，result值是图片路径
            data = {"result": user_profile.photo.url, }
            return JsonResponse(data)

        else:
            return JsonResponse({"msg": "请重新上传。只能上传图片"})

    return redirect('app_user:profile')


