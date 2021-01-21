from django.forms import formset_factory
from django import forms
from django.contrib.auth.models import User
from django.contrib import auth
from .utils import email_check
from .models import UserProfile
from django.core.exceptions import ValidationError
import re
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.conf import settings

# 用户注册
class RegisterForm(UserCreationForm):
    '''注册表单'''
    def __init__(self, *args, **kwargs):
        self._request = kwargs.pop('_request', None)  # 传递额外的参数, 并在调用构造函数之前从 kwargs 中删除额外的参数
        super(RegisterForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget = forms.widgets.TextInput(attrs={"class": "form-control"})
        self.fields['email'].widget = forms.widgets.EmailInput(attrs={"class": "form-control"})
        self.fields['password1'].widget = forms.widgets.PasswordInput(attrs={"class": "form-control"})
        self.fields['password2'].widget = forms.widgets.PasswordInput(attrs={"class": "form-control"})

        # 添加额外的字段 initial="默认值"
        # self.fields['extra_field'].initial ="harvard"
        self.fields['check_code'] = forms.CharField(label='验证码', widget=forms.TextInput(attrs={'placeholder': '不区分大小写', "class": "form-control"}))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email_check(email):
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("邮箱已存在")
        else:
            raise forms.ValidationError("请检查邮箱格式")
        return email

    def clean_check_code(self):
        checkcode = self.cleaned_data.get('check_code')
        if checkcode.lower() != self._request.session['CheckCode'].lower():  # 验证验证码
            raise forms.ValidationError("验证码错误")
        return checkcode

    class Meta:
        model = User
        fields = ("username", "email")


# 用户登录
class LoginForm(forms.Form):
    '''用户登录'''

    username = forms.CharField(label='用户名', max_length=20, min_length=6, widget=forms.TextInput(attrs={'placeholder': '用户名 手机号 邮箱'}))
    password = forms.CharField(label='密码', widget=forms.PasswordInput)
    check_code = forms.CharField(label='验证码', widget=forms.TextInput(attrs={'placeholder': '不区分大小写'}))

    def __init__(self, *args, **kwargs):
        self._request = kwargs.pop('_request', None)  # 传递额外的参数, 并在调用构造函数之前从 kwargs 中删除额外的参数
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean_check_code(self):
        checkcode = self.cleaned_data.get('check_code')
        if not settings.DEBUG:
            if checkcode.lower() != self._request.session['CheckCode'].lower():  # 验证验证码
                raise forms.ValidationError("验证码错误")
        return checkcode


# 修改密码
class PwdChangeForm(forms.Form):
    '''修改密码'''
    username = forms.CharField(widget=forms.HiddenInput)
    old_pw = forms.CharField(label='旧密码', widget=forms.PasswordInput)
    pw1 = forms.CharField(label='新密码', widget=forms.PasswordInput)
    pw2 = forms.CharField(label='再次输入密码', widget=forms.PasswordInput)
    check_code = forms.CharField(
        label='验证码', widget=forms.TextInput(attrs={'placeholder': '不区分大小写'}))

    def clean_old_pw(self):
        old_pw = self.cleaned_data.get('old_pw', '')
        if len(old_pw) < 6:
            raise forms.ValidationError("密码太短。")
        else:
            username = self.cleaned_data.get('username')
            u = auth.authenticate(username=username, password=old_pw)
            if not u:
                raise forms.ValidationError('密码错误。请重试。')
        return old_pw

    def clean_pw1(self):
        pw1 = self.cleaned_data.get('pw1', '')
        if len(pw1) < 6:
            raise forms.ValidationError("密码太短。")
        return pw1

    def clean_pw2(self):
        pw1 = self.cleaned_data.get('pw1')
        pw2 = self.cleaned_data.get('pw2')
        if pw1 and pw2 and pw1 != pw2:
            raise forms.ValidationError("两次密码不一致。")
        return pw2



# 自定义手机号验证
def mobile_validate(value):
    mobile_re = re.compile(r'^(13[0-9]|15[012356789]|17[678]|18[0-9]|14[57])[0-9]{8}$')
    if not mobile_re.match(value):
        raise ValidationError('手机号码格式错误')
# mobile = forms.CharField(validators=[mobile_validate, ], error_messages={'required': u'手机不能为空'},
#                             widget=forms.TextInput(attrs={'class': "form-control", 'placeholder': u'手机号码'}))


# 用户信息编辑(User)
class UserEditForm(forms.ModelForm):
    '''用户信息编辑(User)'''
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        # widgets = {
        #     'first_name': forms.TextInput(attrs={'disabled': 'disabled'}),
        # }
        labels = {
                'email': '邮箱',
                }


# 用户信息编辑(UserProfile)
class ProfileEditForm(forms.ModelForm):
    '''用户信息编辑(UserProfile)'''
    class Meta:
        model = UserProfile
        fields = ('org', 'telephone')

        widgets = {
            'org': forms.Textarea(attrs={'cols': 19, 'rows': 1, 'class': '自定义样式'}),
            'telephone': forms.TextInput(attrs={'type' : 'number','class' : 'your_class', 'max_length': 6, 'placeholder': u'手机号码'})
        }
        labels = {
            'org': 'ORG',
            'telephone': '666'
        }
        help_texts = {
            'org': ('Some useful help text.'),
        }
        error_messages = {
            'org': {
                'max_length': ("This writer's org is too long."),
            },
        }


# 用户头像表单
class UserPhotoUploadForm(forms.Form):
    '''用户头像表单'''
    photo_file = forms.ImageField()

    def clean_photo_file(self):
        photo_file = self.cleaned_data.get('photo_file', '')
        if not re.search(r'\.(png|jpg|jpeg|gif)$', photo_file.name):
            # print('文件类型只能是: png,jpg,jpeg,gif')
            raise forms.ValidationError('文件类型只能是: png,jpg,jpeg,gif')
        return photo_file


















# formset_factory ---------------------------------------------------------------------
# 有的时候用户需要在1个页面上使用多个表单，比如一次性提交添加多本书的信息，这时我们可以使用formset。这是一个表单的集合
# extra: 额外的空表单数量
# max_num: 包含表单数量（不含空表单), max_num优先级高于extra
EditForm = formset_factory(ProfileEditForm, extra=3, max_num=2)  # 创建多个相同的表单

# inlineformset ---------------------------------------------------------------------
# 想我们有如下 recipe 模型，Recipe 与 Ingredient是单对多的关系。
# 一般的formset只允许我们一次性提交多个Recipe或多个Ingredient。
# 但如果我们希望同一个页面上添加一个菜谱(Recipe)和多个原料(Ingredient)，这时我们就需要用使用 inlineformset 了

# models.py
from django.db import models
class Recipe(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()

class Ingredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredient')
    name = models.CharField(max_length=255)

# forms.py
from django.forms import ModelForm
from django.forms import inlineformset_factory
class RecipeForm(ModelForm):
    class Meta:
        model = Recipe
        fields = ("title", "description",)
# 第一个参数必需是ForeignKey
IngredientFormSet = inlineformset_factory(Recipe, Ingredient, fields=('name',),
                                          extra=3, can_delete=False, max_num=5)

# views.py
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render
def recipe_update(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.method == "POST":
        form = RecipeForm(request.POST, instance=recipe)

        if form.is_valid():
            recipe = form.save()
            # 在对 IngredientFormSet 进行实例化的时候，必需指定recipe的实例
            ingredient_formset = IngredientFormSet(request.POST, instance=recipe)

            if ingredient_formset.is_valid():
                ingredient_formset.save()

        return redirect('/recipe/')
    else:
        form = RecipeForm(instance=recipe)
        ingredient_formset = IngredientFormSet(instance=recipe)

    return render(request, 'recipe/recipe_update.html', {'form': form,
                                                         'ingredient_formset': ingredient_formset,
                                                      })

def recipe_add(request):
    if request.method == "POST":
        form = RecipeForm(request.POST)

        if form.is_valid():
            recipe = form.save()
            ingredient_formset = IngredientFormSet(request.POST, instance=recipe)

            if ingredient_formset.is_valid():
                ingredient_formset.save()

        return redirect('/recipe/')
    else:
        form = RecipeForm()
        ingredient_formset = IngredientFormSet()

    return render(request, 'recipe/recipe_add.html', {'form': form,
                                                      'ingredient_formset': ingredient_formset,
                                                      })

# template
'''
<h1>Add Recipe</h1>
<form action="." method="POST">
    {% csrf_token %}

    {{ form.as_p }}

    <fieldset>
        <legend>Recipe Ingredient</legend>
        {{ ingredient_formset.management_form }}
        {{ ingredient_formset.non_form_errors }}
        {% for form in ingredient_formset %}
                {{ form.name.errors }}
                {{ form.name.label_tag }}
                {{ form.name }}
            </div>
      {% endfor %}
    </fieldset>

    <input type="submit" value="Add recipe" class="submit" />
</form>
'''

# 整个formset的验证 ---------------------------------------------------------------------
# 下面例子中用户一次性提交多篇文章标题后，我们需要检查title是否已重复。
# 我们先定义一个BaseFormSet，然后使用formset=BaseArticleFormSet添加formset的验证。
from django.forms import BaseFormSet
from django.forms import formset_factory
# from myapp.forms import ArticleForm

class BaseArticleFormSet(BaseFormSet):
    def clean(self):
        """Checks that no two posts have the same title."""
        if any(self.errors):
            return

        titles = []
        for form in self.forms:
            title = form.cleaned_data['title']
            if title in titles:
                raise forms.ValidationError("Articles in a set must have distinct titles.")
        titles.append(title)

# ArticleFormSet = formset_factory(ArticleForm, formset=BaseArticleFormSet)


# 给Formset添加额外字段 ---------------------------------------------------------------------
# 在BaseFormSet里我们不仅可以添加formset的验证，而且可以添加额外的字段，如下所示:
from django.forms import BaseFormSet
from django.forms import formset_factory
# from myapp.forms import ArticleForm

class BaseArticleFormSet(BaseFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)
        form.fields["my_field"] = forms.CharField()
          
# ArticleFormSet = formset_factory(ArticleForm, formset=BaseArticleFormSet)



