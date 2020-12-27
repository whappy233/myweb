from django import forms
from django.contrib.auth.models import User
from django.contrib import auth
from .utils import email_check
from .models import UserProfile


# 用户注册
class RegistrationForm(forms.Form):

    username = forms.CharField(label='用户名', max_length=20, min_length=6)
    email = forms.EmailField(label='邮箱')
    password1 = forms.CharField(label='密码', widget=forms.PasswordInput)
    password2 = forms.CharField(label='再次输入密码', widget=forms.PasswordInput)
    check_code = forms.CharField(
        label='验证码', widget=forms.TextInput(attrs={'placeholder': '不区分大小写'}))

    def clean_username(self):
        username = self.cleaned_data.get('username')
        filter_result = User.objects.filter(username__exact=username)
        if len(filter_result) > 0:
            raise forms.ValidationError("用户名已存在.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email_check(email):
            filter_result = User.objects.filter(email__exact=email)
            if len(filter_result) > 0:
                raise forms.ValidationError("邮箱已存在。")
        else:
            raise forms.ValidationError("请检查邮箱格式。")
        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 6:
            raise forms.ValidationError("密码太短。")
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("两次密码不一致。")
        return password2


# 用户登录
class LoginForm(forms.Form):
    username = forms.CharField(label='用户名', max_length=20, min_length=6,
                            widget=forms.TextInput(attrs={
                                    'placeholder': '用户名 手机号 邮箱'
                            }))
    password = forms.CharField(label='密码', widget=forms.PasswordInput)
    check_code = forms.CharField(
        label='验证码', widget=forms.TextInput(attrs={'placeholder': '不区分大小写'}))


# 修改密码
class PwdChangeForm(forms.Form):
    username = forms.CharField(widget=forms.HiddenInput)
    old_pw = forms.CharField(label='旧密码', widget=forms.PasswordInput)
    pw1 = forms.CharField(label='新密码', widget=forms.PasswordInput)
    pw2 = forms.CharField(label='再次输入密码', widget=forms.PasswordInput)
    check_code = forms.CharField(
        label='验证码', widget=forms.TextInput(attrs={'placeholder': '不区分大小写'}))

    def clean_old_pw(self):
        old_pw = self.cleaned_data.get('old_pw')
        if len(old_pw) < 6:
            raise forms.ValidationError("密码太短。")
        else:
            username = self.cleaned_data.get('username')
            u = auth.authenticate(username=username, password=old_pw)
            if not u:
                raise forms.ValidationError('密码错误。请重试。')
        return old_pw

    def clean_pw1(self):
        pw1 = self.cleaned_data.get('pw1')
        if len(pw1) < 6:
            raise forms.ValidationError("密码太短。")
        return pw1

    def clean_pw2(self):
        pw1 = self.cleaned_data.get('pw1')
        pw2 = self.cleaned_data.get('pw2')
        if pw1 and pw2 and pw1 != pw2:
            raise forms.ValidationError("两次密码不一致。")
        return pw2


# 用户信息编辑(User)
class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        # widgets = {
        #     'first_name': forms.TextInput(attrs={'disabled': 'disabled'}),
        # }

# 用户信息编辑(UserProfile)
class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('org', 'telephone')

# 用户头像表单
class UserPhotoUploadForm(forms.Form):
    photo_file = forms.ImageField()


from  django.forms import formset_factory
# 有的时候用户需要在1个页面上使用多个表单，比如一次性提交添加多本书的信息，这时我们可以使用formset。这是一个表单的集合
# extra: 额外的空表单数量
# max_num: 包含表单数量（不含空表单)
EditForm = formset_factory(ProfileEditForm, extra=3, max_num=2)
