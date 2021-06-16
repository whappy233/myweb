import io

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse, HttpResponseBadRequest
from django.http.response import Http404, HttpResponseServerError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.edit import FormView
from django.contrib.auth.forms import UserCreationForm
from loguru import logger
from myweb.utils import GenerateEncrypted, get_current_site

from .models import UserProfile
from .utils import create_validate_code as CheckCode
from .utils import crop_image, generate_vcode, send_email

from .forms import (EditForm, LoginForm, ProfileEditForm, PwdChangeForm,
                    RegisterForm, UserEditForm, UserPhotoUploadForm)

# from app_common.decorators import check_honeypot, honeypot_exempt

from app_common.utils import get_blog_setting

from .utils import validateEmail

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
        return HttpResponse(f"请求异常：{repr(e)}")



# 注册
@method_decorator(never_cache, name='dispatch')
class RegisterView(FormView):
    form_class = RegisterForm
    template_name = 'tp/用户验证.html'

    def get(self, request, *args, **kwargs):
        '''处理GET请求：实例化表单的空白版本'''
        if request.user.is_authenticated:
            return redirect('app_blog:article_list')
        return super(RegisterView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        if get_blog_setting().allow_register:
            return super(RegisterView, self).post(request, *args, **kwargs)
        else:
            return self.render_to_response(self.get_context_data(err_message='网站已停止注册'))

    def get_form_kwargs(self):
        '''给 Form 表单传递额外的参数'''
        kwargs = super(RegisterView, self).get_form_kwargs()
        kwargs['_request'] = self.request
        return kwargs

    def get_success_url(self, id=None):
        """表单验证成功后，返回要重定向的URL"""
        if id:
            return f"{reverse('app_user:register_result')}?type=register&id={id}"
        return '/'

    def form_invalid(self, form):
        """表单验证失败 render."""
        username = self.request.POST.get('username', '')
        err_message = '\n'.join(v[0] for v in form.errors.values())
        return self.render_to_response(self.get_context_data(err_message=err_message, r_username = username))

    def get_context_data(self, **kwargs):
        """在 context 添加新的值."""
        kwargs['is_register'] = True
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        '''当表单验证成功 redirect'''

        user = form.save(False)
        user.is_active = False
        user.save(True)
        return redirect(self.get_success_url(user.id))

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


# ajax 注册
def ajax_register(request):
    if request.method == 'POST' and request.is_ajax():
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(False)
            user.is_active = False
            user.save(True)

            site = get_current_site().domain
            sign = GenerateEncrypted.encode({'id':user.id})
            if settings.DEBUG: site = '127.0.0.1:8000'
            path = reverse('app_user:register_result')
            url = f"http://{site}{path}?type=validation&id={user.id}&sign={sign}"
            text = f'<p>点击下面链接验证您的邮箱</p><a href="{url}" rel="bookmark">{url}</a>'
            print(text)
            send_email(to_email=user.email, vcode_str=text)
            msg = f'恭喜您注册成功，一封验证邮件已经发送到 {user.email} ，请验证邮箱后登录本站!'
            return JsonResponse({'status':200, 'msg':msg})

        else:
            err_msg = []
            for msg in form.errors.as_data().values():
                err_msg.extend(msg[0].messages)
            return JsonResponse({'status':400, 'msg':'<br>'.join(err_msg)})
    return JsonResponse({'status':400, 'msg':'FAIL'})


# 登录
# @check_honeypot(field_name='12223')
@never_cache
@sensitive_post_parameters('password')  # 记录未处理的异常时将password隐藏
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

    next = request.GET.get('next', '')
    if not next.strip():
        next = reverse('app_blog:article_list')

    message = ''
    username = request.POST.get('username', '')
    if request.method == 'POST':

        form = LoginForm(request.POST, _request=request)  #  _request 的目的是将 session(其中包含验证码) 传递给表单

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = auth.authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    auth.login(request, user)
                    try:
                        return redirect(next)
                    except:
                        return redirect('/')
                else:
                    url =f"{reverse('app_user:register_result')}?type=register&id={user.id}"
                    message = f'账户未激活, 请激活后再登录.<br><a href="{url}"> 点击发送激活链接到邮箱({user.email})</a>'
            else:
                message = '用户名或密码错误, 请重试'
        else:
            message = '\n'.join(v[0] for v in form.errors.values())

    return render(request, 'tp/用户验证.html', {'username': username, 'message': message})


# ajax 登录
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def ajax_login(request):
    if request.method == 'POST' and request.is_ajax():
        # 在前端发送ajax json 请求时(application/json;charset=UTF-8), 数据存放在request.body中,  request.POST, 没有数据.
        print(request.body)  # --> b'{"username":"891953720","password":"wu910hao"}'

        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = auth.authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    auth.login(request, user)
                    return JsonResponse({'status':200,'msg':'登录成功'})
                else:
                    url =f"{reverse('app_user:register_result')}?type=register&id={user.id}"
                    message = f'账户未激活, 请激活后再登录.<br><a href="{url}"> 点击发送激活链接到邮箱({user.email})</a>'
                    return JsonResponse({'status':400,'msg':message})
            else:
                return JsonResponse({'status':400,'msg': '用名户或密码错误。请重试'})
        else:
            message = '\n'.join(v[0] for v in form.errors.values())
            return JsonResponse({'status':400,'msg':message})
    else:
        return HttpResponseForbidden()



from django.contrib.auth import views as auth_views
# 退出登录
def logout(request):
    before = request.GET.get('before', reverse('app_blog:article_list'))
    return auth_views.LogoutView.as_view(next_page=before)(request)


# 修改密码
@never_cache
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



# 注册成功发送验证邮件以及邮箱验证
def register_result(request):
    '''注册成功以及邮箱验证'''
    type = request.GET.get('type')
    id = request.GET.get('id')
    user = get_object_or_404(User, id=id)
    logger.info(type)
    if user.is_active:
        return redirect('/')

    if type and type in ['register', 'validation']:
        if type == 'register':
            # 注册成功 等待激活
            site = get_current_site().domain
            sign = GenerateEncrypted.encode({'id':user.id})
            if settings.DEBUG: site = '127.0.0.1:8000'
            path = reverse('app_user:register_result')
            url = f"http://{site}{path}?type=validation&id={user.id}&sign={sign}"
            text = f'<p>请点击下面链接验证您的邮箱</p><a href="{url}" rel="bookmark">{url}</a>'
            print(text)
            send_email(to_email=user.email, vcode_str=text)
            content = f'恭喜您注册成功，一封验证邮件已经发送到您 {user.email} 的邮箱，请验证您的邮箱后登录本站。'
            title = '注册成功'
            return render(request, 'app_user/register_result.html', {'title': title, 'content': content})
        else:
            # 邮箱点击激活
            sign = request.GET.get('sign')
            if sign:
                data = GenerateEncrypted.decode(sign)
                if data:
                    if data.get('id', -1) == user.id:
                        user.is_active = True
                        user.save(update_fields=['is_active'])
                        content = '恭喜您完成邮箱验证，您现在可以使用您的账号来登录本站。'
                        title = '验证成功'
                        return render(request, 'app_user/register_result.html', {'title': title, 'content': content})
            return HttpResponseForbidden()
    else:
        return redirect('/')


# Ajax 发送邮箱验证码
def send_email_vcode(request):
    if request.method == 'POST':
        email = request.POST.get('email', None)

        if not validateEmail(email):
            return JsonResponse({'status':400, 'msg':'请输入一个有效的 Email 地址!'})

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
                return JsonResponse({'status':200,'msg':'验证码发送成功，请注意查收!'})
            else:
                return JsonResponse({'status':400,'msg':'发送验证码出错，请重试!'})
        else:
            return JsonResponse({'status':400,'msg':'电子邮箱不存在!'})
    else:
        return JsonResponse({'status':400,'msg':'方法错误!'})


# 忘记密码
def forget_pwd_(request):
    if request.method == 'GET':
        return render(request, 'app_user/forget_pwd.html')
    elif request.method == 'POST':
        email = request.POST.get("email", None)  # 邮箱
        vcode = request.POST.get("vcode", None)  # 验证码
        new_pwd= request.POST.get('pw1', None)  # 密码
        new_pwd_confirm = request.POST.get('pw2')
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


def forget_pwd(request):
    if request.method == 'POST' and request.is_ajax():
        email = request.POST.get("email", None)  # 邮箱
        vcode = request.POST.get("vcode", None)  # 验证码
        new_pwd= request.POST.get('pw1', None)  # 密码
        new_pwd_confirm = request.POST.get('pw2', None)
        # 查询验证码和邮箱是否匹配
        if new_pwd != new_pwd_confirm:
            return JsonResponse({'status':400, 'msg':'两次密码不一致'})
        try:
            s_data = request.session.get('vcode', None)
            s_email = request.session.get('email', None)
            if s_data and s_email:
                if s_data==vcode and s_email==email:
                    user = User.objects.get(email=email)
                    print(new_pwd)
                    user.set_password(new_pwd)
                    user.save()
                    request.session.flush()
                    message = f"修改密码成功，去<a href='{reverse('app_user:login')}'>登录</a>！"
                    return JsonResponse({'status': 200, 'msg': message})
                else:
                    return JsonResponse({'status': 400, 'msg': "验证码错误"})
            else:
                return JsonResponse({'status': 400, 'msg': "验证码过期"})
        except Exception as e:
            return JsonResponse({'status': 400, 'msg': "验证码错误"})

    return HttpResponseForbidden()


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
            cropped_photo = crop_image(old_photo, photo, data, user.profile.uuid)  # 剪裁保存图片
            user_profile.photo = cropped_photo  # 将图片路径修改到当前用户数据库
            user_profile.save()

            # 向前台返回一个json，result值是图片路径
            data = {"result": user_profile.photo.url, }
            print(data)
            return JsonResponse(data)

        else:
            return JsonResponse({"msg": "请重新上传。只能上传图片"})

    return redirect('app_user:profile')

