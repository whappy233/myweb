import io

from django.contrib import auth
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse, JsonResponse, Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic.edit import FormView
from .forms import (EditForm, LoginForm, ProfileEditForm, PwdChangeForm,
                    UserEditForm, UserPhotoUploadForm, RegisterForm)
from app_user.models import UserProfile
from app_user.utils import crop_image, generate_vcode, send_email, create_validate_code as CheckCode
from myweb.utils import get_current_site, get_md5
from django.conf import settings
from loguru import logger

# from app_common.decorators import check_honeypot, honeypot_exempt



# 自定义验证后端
class CustomBackend(ModelBackend):
    """实现用户名邮箱手机号登录"""
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 不希望用户存在两个，get只能有一个。两个是get失败的一种原因 Q为使用并集查询
            user = User.objects.get(Q(username=username) | Q(email=username) | Q(profile__telephone=username))
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



def user_result(request):
    type = request.GET.get('type')
    id = request.GET.get('id')

    user = get_object_or_404(User, id=id)
    logger.info(type)
    if user.is_active:
        return redirect('/')
    if type and type in ['register', 'validation']:
        if type == 'register':
            content = f'恭喜您注册成功，一封验证邮件已经发送到您 {user.email} 的邮箱，请验证您的邮箱后登录本站。'
            title = '注册成功'
        else:
            c_sign = get_md5(get_md5(settings.SECRET_KEY + str(user.id)))
            sign = request.GET.get('sign')
            if sign != c_sign:
                return HttpResponseForbidden()
            user.is_active = True
            user.save()
            content = '恭喜您已经成功的完成邮箱验证，您现在可以使用您的账号来登录本站。'
            title = '验证成功'
        return render(request, 'app_user/result.html', {'title': title, 'content': content})
    else:
        return redirect('/')



# 注册
class RegisterView(FormView):
    form_class = RegisterForm
    template_name = 'app_user/registration.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('app_blog:article_list')
        return super(RegisterView, self).get(request, *args, **kwargs)

    def get_form_kwargs(self):
        '''给 Form 表单传递额外的参数'''
        kwargs = super(RegisterView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        if form.is_valid():
            user = form.save(False)
            user.is_active = False
            user.save(True)

            site = get_current_site().domain
            sign = get_md5(get_md5(settings.SECRET_KEY + str(user.id)))
            if settings.DEBUG: site = '127.0.0.1:8000'
            path = reverse('app_user:result')
            url = f"http://{site}{path}?type=validation&id={user.id}&sign={sign}"
            content = f'<p>请点击下面链接验证您的邮箱</p><a href="{url}" rel="bookmark">{url}</a>再次感谢您！<br />如果上面链接无法打开，请将此链接复制至浏览器。{url}'
            print(content)
            send_email(to_email=user.email, vcode_str=content)
            url =f"{reverse('app_user:result')}?type=register&id={user.id}"
            return redirect(url)

            # username = form.cleaned_data['username']
            # email = form.cleaned_data['email']
            # password = form.cleaned_data['password2']
            # 使用内置User自带create_user方法创建用户，不需要使用save()
            # User.objects.create_user(username=username, password=password, email=email)
            # 1.通过 signals, 在创建 User 对象实例时也创建 UserProfile 对象实例
            # 2.或在创建User时同时创建与之关联的UserProfile对象
            # user_profile = UserProfile(user=user)
            # 如果直接使用objects.create()方法后不需要使用save()
            # user_profile.save()
            return redirect("app_user:login")  # 注册成功, 跳转到登录
        return self.render_to_response({'form': form})


# 登录
# @check_honeypot(field_name='12223')
def login(request):
    '''登录'''
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

    # 如果登录用户访问注册页面，跳转到首页
    if request.user.is_authenticated:
        return redirect('app_blog:article_list')

    next = request.GET.get('next', reverse('app_blog:article_list'))

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
            if user:
                if user.is_active:
                    auth.login(request, user)
                    return redirect(next)
                else:
                    message = '用户被禁用！'
            else:
                message = '密码错误。请重试。'
    else:
        form = LoginForm()
    return render(request, 'app_user/login.html', {'form': form, 'message': message})

# 修改密码
@login_required
def change_pw(request):
    '''修改密码'''
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
                return redirect('app_user:login')
            else:
                message = '密码错误。请重试。'
    else:
        form = PwdChangeForm(initial={'username': request.user.username})

    return render(request, 'app_user/change_pw.html', {'form': form, 'message': message})

# Ajax 发送邮箱验证码
def send_email_vcode(request):
    if request.method == 'POST':
        email = request.POST.get('email',None)
        is_email = User.objects.filter(email=email)
        if is_email.count() != 0:
            vcode_str = generate_vcode()
            # 发送邮件
            send_status = send_email(to_email=email, vcode_str=vcode_str)
            if send_status:
                request.session['email'] = email
                request.session['vcode'] = vcode_str
                request.session.set_expiry(300)
                print(f'邮箱验证码: {vcode_str}')
                return JsonResponse({'status':True,'data':'发送成功'})
            else:
                return JsonResponse({'status':False,'data':'发送验证码出错，请重试！'})
        else:
            return JsonResponse({'status':False,'data':'电子邮箱不存在！'})
    else:
        return JsonResponse({'status':False,'data':'方法错误'})

# 忘记密码
def forget_pwd(request):
    if request.method == 'GET':
        return render(request, 'app_user/forget_pwd.html')
    elif request.method == 'POST':
        email = request.POST.get("email", None)  # 邮箱
        vcode = request.POST.get("vcode", None)  # 验证码
        new_pwd= request.POST.get('password', None)  # 密码
        new_pwd_confirm = request.POST.get('confirm_password')
        # 查询验证码和邮箱是否匹配
        try:
            s_data = request.session.get('vcode', None)
            s_email = request.session.get('email', None)
            if s_data and s_email:
                if s_data==vcode and s_email==email:
                    user = User.objects.get(email=email)
                    user.set_password(new_pwd)
                    user.save()
                    request.session.flush()
                    message = f"修改密码成功，去<a href='{reverse('app_user:login')}'>登录</a>！"
                    return render(request, 'app_user/forget_pwd.html', {'msg': message})
                else:
                    message = "验证码错误"
                    return render(request, 'app_user/forget_pwd.html', {'msg': message})
            else:
                message = "验证码过期"
                return render(request, 'app_user/forget_pwd.html', {'msg': message})
        except Exception as e:
            message = "验证码错误"
            return render(request,'app_user/forget_pwd.html', {'msg': message})

# 编辑资料
@login_required
def profile(request):
    '''资料编辑'''
    message = ''
    if request.method == 'POST':
        user_form = UserEditForm(data=request.POST, instance=request.user)
        profile_form = ProfileEditForm(data=request.POST, files=request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            message = '信息修改成功'
        else:
            info = profile_form.errors.get_json_data()
            message = '修改失败: ' + ''.join(l['message'] for i in info.values() for l in i)
    else:
        try:
            user_form = UserEditForm(instance=request.user)  # 初始化表单
            profile_form = ProfileEditForm(instance=request.user.profile)
        except Exception as e:
            err_info = f'ERROR Info: {e}<br>请检查是否关联了UserProfile(OneToOneField)'
            return HttpResponse(err_info)

    return render(request, 'app_user/profile.html',
                  context={
                      'user_form': user_form,
                      'profile_form': profile_form,
                      'message': message})

# Ajax 上传头像
@login_required
def ajax_photo_upload(request):
    '''头像上传'''
    user = request.user
    user_profile = get_object_or_404(UserProfile, user=user)

    if request.method == "POST":
        form = UserPhotoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            photo = request.FILES['photo_file']  # 获取上传图片
            data = request.POST['photo_data']  # 获取ajax返回图片坐标 {"x":0,"y":0,"width":80,"height":80,"rotate":0,"scaleX":1,"scaleY":1}

            if photo.size/1024 > 3000:
                return JsonResponse({"msg": "图片大小请控制在3M以内, 请重新上传。", })

            old_photo = user_profile.photo  # 旧的头像
            cropped_photo = crop_image(old_photo, photo, data, user.id)  # 剪裁保存图片
            user_profile.photo = cropped_photo  # 将图片路径修改到当前用户数据库
            user_profile.save()

            # 向前台返回一个json，result值是图片路径
            data = {"result": user_profile.photo.url, }
            return JsonResponse(data)

        else:
            return JsonResponse({"msg": "请重新上传。只能上传图片"})

    return redirect('app_user:profile')


