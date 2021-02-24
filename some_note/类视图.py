

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
