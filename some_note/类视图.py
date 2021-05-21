

'''get_queryset()方法'''
# 该方法可以返回一个量身定制的对象列表。
# 当我们使用Django自带的 ListView 展示所有对象列表时，ListView 默认会返回 Model.objects.all()。
# 当我们希望只展示作者自己发表的文章列表且按文章发布时间逆序排列时，
# 我们就可以通过更具体的 get_queryset 方法来返回一个我们想要显示的对象列表。
from django.views.generic import ListView
from app_blog.models import Article
from django.utils import timezone
class IndexView(ListView):
    template_name = 'blog/article_list.html'
    context_object_name = 'recently_updated'
    # 希望只展示作者自己发表的文章列表且按文章发布时间逆序排列
    def get_queryset(self):
        return Article.objects.filter(author = self.request.user).order_by('-pub_date')


'''get_context_data()'''
# get_context_data可以用于给模板传递模型以外的内容或参数
from django.views.generic import ListView
from app_blog.models import Article
from django.utils import timezone
class IndexView(ListView):
    queryset = Article.objects.all().order_by("-pub_date")
    template_name = 'blog/article_list.html'
    context_object_name = 'recently_updated'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now() #只有这行代码有用
        return context


'''get_object()方法'''
# DetailView 和 EditView 都是从URL根据pk或其它参数调取一个对象来进行后续操作。
# 你希望一个用户只能查看或编辑自己发表的文章对象。
# 当用户查看别人的对象时，返回http 404错误。
# 这时候你可以通过更具体的get_object()方法来返回一个更具体的对象。代码如下:
from django.views.generic import DetailView
from django.http import Http404
from app_blog.models import Article
from django.utils import timezone
class ArticleDetailView(DetailView):
    queryset = Article.objects.all().order_by("-pub_date")
    template_name = 'blog/article_detail.html'
    context_object_name = 'article'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if obj.author != self.request.user:
            raise Http404()
        return obj


from django.http import JsonResponse
from django.views import View
class OrderView(View):
    """登陆后可以访问"""
    def get(self, request, *args, **kwargs):
        # 打印用户jwt信息
        print(request.user_info)
        return JsonResponse({'data': '订单列表'})

    def post(self, request, *args, **kwargs):
        print(request.user_info)
        return JsonResponse({'data': '添加订单'})

    def put(self, request, *args, **kwargs):
        print(request.user_info)
        return JsonResponse({'data': '修改订单'})

    def delete(self, request, *args, **kwargs):
        print(request.user_info)
        return JsonResponse({'data': '删除订单'})




# forms.py -------------------------------------
from django.forms import ModelForm,  TextInput, URLInput, ClearableFileInput
from .models import Restaurant, Dish
class RestaurantForm(ModelForm):
    class Meta:
        model = Restaurant
        exclude = ('user', 'date',)

        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
            'address': TextInput(attrs={'class': 'form-control'}),
            'telephone': TextInput(attrs={'class': 'form-control'}),
            'url': URLInput(attrs={'class': 'form-control'}),
        }

        labels = {
            'name': '名称',
            'address': '地址',
            'telephone': '电话',
            'url': '网站',
        }

# views.py --------------------------------------
from django.views.generic.edit import CreateView
class RestaurantCreate(CreateView):
    model = Restaurant
    template_name = 'myrestaurants/form.html'
    form_class = RestaurantForm

    # Associate form.instance.user with self.request.user
    # form_valid方法作用是添加前端表单字段以外的信息。
    # 在用户在创建餐厅时，我们不希望用户能更改创建用户，于是在前端表单里把user故意除外了(见forms.py)，而选择在后台添加user信息
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(RestaurantCreate, self).form_valid(form)

# template
'''
    {% extends "myrestaurants/base.html" %}
    {% block content %}
    <form action="" method="POST" enctype="multipart/form-data" >
        {% csrf_token %}
        {% for hidden_field in form.hidden_fields %}
        {{ hidden_field }}
    {% endfor %}
    {% if form.non_field_errors %}
        <div class="alert alert-danger" role="alert">
        {% for error in form.non_field_errors %}
            {{ error }}
        {% endfor %}
        </div>
    {% endif %}
    {% for field in form.visible_fields %}
        <div class="form-group">
        {{ field.label_tag }}
        {{ field }}
        {% if field.help_text %}
            <small class="form-text text-muted">{{ field.help_text }}</small>
        {% endif %}
        </div>
    {% endfor %}
        <input type="submit" value="提交"/>
    </form>
    {% endblock %}
'''


# ------------------------------------------------------------------------------------
# 类视图装饰器
def zzz(text='类视图装饰器'):
    from django.contrib.auth.decorators import login_required
    from django.utils.decorators import method_decorator
    from django.views.generic import TemplateView

    # 关键参数 name 传递要被装饰的方法名:
    # 因为所有的请求必须经过 dispatch 方法, 所以相当于所有请求都需要 login_required 验证
    @method_decorator(login_required, name='dispatch')
    class ProtectedView(TemplateView):
        template_name = 'secret.html'

    # decorator 参数接受一个装饰器列表或元组
    from django.views.decorators.cache import never_cache
    decorators = [never_cache, login_required]
    @method_decorator(decorators, name='dispatch')
    class ProtectedView(TemplateView):
        template_name = 'secret.html'


# ------------------------------------------------------------------------------------
# 基于类的通用视图
def zzz(text='基于类的通用视图'):
    from django.shortcuts import redirect
    from django.shortcuts import render
    from django.views import View
    from .forms import MyForm

    class MyFormView(View):
        form_class = MyForm
        initial = {'key': 'value'}
        template_name = 'form_template.html'

        def get(self, request, *args, **kwargs):
            form = self.form_class(initial=self.initial)
            return render(request, self.template_name, {'form': form})

        def post(self, request, *args, **kwargs):
            form = self.form_class(request.POST)
            if form.is_valid():
                # <process form cleaned data>
                return redirect('/success/')
            return render(request, self.template_name, {'form': form})


    # urls 传递的的参数在: self.kwargs 里面(dict)

    # path('authors/<int:pk>/', AuthorDetailView.as_view(), name='author-detail')
    # path('authors/<slug:slug>/', AuthorDetailView.as_view(), name='author-detail')
    # URLconf 在这里使用组 pk ，这个名字是 DetailView 用来查找过滤查询集的主键值的默认名称(pk_url_kwarg),
    # URLconf 在这里使用组 slug ，这个名字是 DetailView 用来查找过滤查询集的slug的默认名称(slug_url_kwarg),
    # 在 DetailView 视图中会自动查找, 不需要手动执行 self.kwargs['pk'] 和 self.kwargs['slug'].
    # 对于继承了 SingleObjectMixin 的视图都支持 pk_url_kwarg 和 slug_url_kwarg, 即需要获取单个对象的视图都支持.

    # 指向用户详情
    class AuthorDetailView(DetailView):
        queryset = User.objects.all()

        def get_object(self):
            obj = super().get_object()  # 这里根据 pk 或 slug 查询对象
            # Record the last accessed date
            obj.last_accessed = timezone.now()
            obj.save()
            return obj


# ------------------------------------------------------------------------------------
# 基于类的Form视图
def zzz(text='基于类的Form视图'):
    from myapp.forms import ContactForm
    from django.views.generic.edit import FormView
    class ContactView(FormView):
        template_name = 'contact.html'
        success_url = '/thanks/'  # 若不提供该属性, 在可能的情况下将会使用 get_absolute_url()

        form_class = ContactForm

        def form_valid(self, form):
            # 验证有效的表单数据后，将调用此方法
            # 返回 HttpResponse 对象
            form.send_email()
            return super().form_valid(form)  # 默认将会重定向到 success_url

    # 示例
    from django.urls import reverse_lazy
    from django.views.generic.edit import CreateView, DeleteView, UpdateView
    from myapp.models import Author

    class AuthorCreate(CreateView):
        model = Author

        # 如果已经给出了 model 属性，则使用这个模型类自动创建 ModelForm
        # 如果 get_object() 返回一个对象，则使用这个对象的类自动创建 ModelForm
        # 如果已经给出了 queryset  ，则使用这个查询集的模型自动创建 ModelForm

        # 在自动生成 ModelForm 的中包含的字段, 在没有指定 form_class 时是必需的
        # 如果同时指定了 fields 和 form_class 属性，将会引发 ImproperlyConfigured 异常
        fields = ['name']  

    class AuthorUpdate(UpdateView):
        model = Author

        # 如果已经给出了 model 属性，则使用这个模型类自动创建 ModelForm
        # 如果 get_object() 返回一个对象，则使用这个对象的类自动创建 ModelForm
        # 如果已经给出了 queryset  ，则使用这个查询集的模型自动创建 ModelForm

        # 在自动生成 ModelForm 的中包含的字段, 在没有指定 form_class 时是必需的
        # 如果同时指定了 fields 和 form_class 属性，将会引发 ImproperlyConfigured 异常
        fields = ['name']

    class AuthorDelete(DeleteView):
        model = Author
        # 使用 reverse_lazy() 来代替 reverse() ，因为在文件导入时不加载 urls
        success_url = reverse_lazy('author-list')


    # 下面是一个展示了如何实现适用于 AJAX 请求的表单以及普通表单的 POST 请求：
    from django.http import JsonResponse
    from django.views.generic.edit import CreateView
    from myapp.models import Author

    class AjaxableResponseMixin:
        """
        添加 Ajax 支持
        必须与基于 FormView 的视图一起使用（例如 CreateView)
        """
        def form_invalid(self, form):
            '''无效表单'''
            response = super().form_invalid(form)
            if self.request.is_ajax():
                return JsonResponse(form.errors, status=400)
            else:
                return response

        def form_valid(self, form):
            '''表单验证成功'''
            # 确保调用父级的 form_valid() 方法
            # 因为它可能会做一些处理(例如在CreateView的情况下, 它将调用form.save() )
            response = super().form_valid(form)
            if self.request.is_ajax():
                data = {'pk': self.object.pk,}
                return JsonResponse(data)
            else:
                return response

    class AuthorCreate(AjaxableResponseMixin, CreateView):
        model = Author
        fields = ['name']

