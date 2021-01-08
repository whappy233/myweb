import django
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.http.response import HttpResponse, JsonResponse, Http404
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods

from django.utils import timezone


from app_blog.models import Article, Comment, Category
from app_user.models import UserProfile

from .forms import ArticleCreateForm






def admin_user(request):
    if request.method == 'GET':
        # user_list = User.objects.all()
        return render(request, 'app_admin/admin_user.html', locals())
    elif request.method == 'POST':
        username = request.POST.get('username','')
        if username == '':
            user_data = User.objects.all().values_list(
                'id','last_login','is_superuser','username','email','date_joined','is_active','first_name'
            )
        else:
            user_data = User.objects.filter(username__icontains=username).values_list(
                'id','last_login','is_superuser','username','email','date_joined','is_active','first_name'
            )
        table_data = []
        for i in list(user_data):
            item = {
                'id':i[0],
                'last_login':i[1],
                'is_superuser':i[2],
                'username':i[3],
                'email':i[4],
                'date_joined':i[5],
                'is_active':i[6],
                'first_name':i[7]
            }
            table_data.append(item)
        return JsonResponse({'status':True,'data':table_data})
    else:
        return JsonResponse({'status':False,'data':'方法错误'})




# Admin -------------------------------------------------

# 所有文章列表
# 权限名一般由app名(app_label)，权限动作和模型名组成。以 app_blog 应用为例，Django为 Article 模型自动创建的4个可选权限名分别为:
# 查看文章(view): app_blog.view_article
# 创建文章(add): app_blog.add_article
# 更改文章(change): app_blog.change_article
# 删除文章(delete): app_blog.delete_article
# 在视图中可以使用 user.has_perm() 方法来判断一个用户是不是有相应的权限, 
# user_A.has_perm('app_blog.add_article')
# user_A.has_perm('app_blog.change_article)

# 最快捷的方式是使用 @permission_required 这个装饰器
# permission_required(perm, login_url=None, raise_exception=False)
# raise_exception=True, 会直接返回403无权限的错误
# 没有权限将会跳转到 login_url='app_blog:article_list'

# 如果你使用基于类的视图(Class Based View), 可以继承PermissionRequiredMixin这个类
# from django.contrib.auth.mixins import PermissionRequiredMixin
# class MyView(PermissionRequiredMixin, View):
    # permission_required = 'polls.can_vote'
    # Or multiple of permissions:
    # permission_required = ('polls.can_open', 'polls.can_edit')



@method_decorator(login_required, name='dispatch')  # 此页面需要登录
@method_decorator(permission_required('app_blog.delete_article', 'app_blog:article_list'), name='dispatch')  # 此页面需要验证权限
class AdminArticleListView(ListView):
    '''文章列表'''
    paginate_by = 10
    template_name = 'app_admin/blog/blog_list.html'

    def get_queryset(self):
        return Article.objects.all().order_by('-publish')

    # def get(self, request, *args, **kwargs):

    #     show_publish = self.request.GET.get('draft')
    #     if show_publish:
    #         articles = Article.objects.filter(status='p').order_by('-publish')
    #     else:
    #         articles = Article.objects.filter(status='d').order_by('-publish')
    #     paginator = Paginator(articles, 5)
    #     page = self.request.GET.get('page')
    #     page_obj = paginator.get_page(page)
    #     context = {
    #         'page_obj': page_obj,
    #         'show_publish': show_publish
    #     }
        # return render(request, 'admin/blog/article_list.html', context)



# 创建文章
# create_blog/
@method_decorator(login_required, name='dispatch')
class ArticleCreateView(CreateView):
    '''创建文章'''
    model = Article
    form_class = ArticleCreateForm
    template_name = 'app_admin/blog/create_blog.html'
    success_url = reverse_lazy('app_admin:admin_blog_list')  # 成功后跳转地址

    # Associate form.instance.user with self.request.user
    def form_valid(self, form):
        form.instance.author = self.request.user
        # print(form.cleaned_data)
        return super().form_valid(form)


# 修改文章
@method_decorator(login_required, name='dispatch')
class ArticleUpdateView(UpdateView):
    '''修改文章'''
    model = Article
    # form_class = ArticleForm
    template_name = 'app_admin/blog/blog_update_form.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if obj.author != self.request.user:
            raise Http404()
        return obj

# 删除文章
@method_decorator(login_required, name='dispatch')
class ArticleDeleteView(DeleteView):
    '''删除文章'''
    model = Article
    success_url = reverse_lazy('app_blog:article_list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if obj.author != self.request.user:
            raise Http404()
        return obj

# 发表文章
@login_required()
def article_publish(request, pk, slug1):
    '''发表文章'''
    article = get_object_or_404(Article, pk=pk, author=request.user)
    article.to_publish()
    return redirect(reverse("app_blog:article_detail", args=[str(pk), slug1]))

