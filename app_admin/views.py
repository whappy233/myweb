from django.contrib.auth.decorators import (login_required,
                                            permission_required,
                                            user_passes_test)
from django.contrib.auth.models import User
from django.http.response import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.db.models import Q

from app_blog.models import Article, Category, Comment
from app_user.models import UserProfile
from .decorators import superuser_only
from .forms import ArticleCreateForm



@method_decorator(superuser_only('app_user:login'), name='dispatch')  # 超级管理员验证
def index(request):
    return render(request, 'app_admin/index.html')


# 所有文章列表
# blog/
@method_decorator(superuser_only('app_user:login'), name='dispatch')  # 超级管理员验证
@method_decorator(login_required, name='dispatch')  # 此页面需要登录
class AdminArticleListView(ListView):
    '''文章列表'''
    paginate_by = 10
    template_name = 'app_admin/blog/blog_list.html'

    def get_queryset(self):
        obj = Article.objects.filter(is_delete=False).order_by('-publish')
        self.search_key__ = self.request.GET.get('search')
        if self.search_key__:
            obj = obj.filter(Q(title__icontains=self.search_key__)|Q(body__icontains=self.search_key__))
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.search_key__
        return context


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


class Common:
    model = Article
    form_class = ArticleCreateForm
    template_name = 'app_admin/blog/create_updata_blog.html'
    success_url = reverse_lazy('app_admin:blog_list')  # 成功后跳转地址


# 创建文章 blog/create
@method_decorator(login_required, name='dispatch')
class ArticleCreateView(Common, CreateView):
    '''创建文章'''

    # Associate form.instance.user with self.request.user
    def form_valid(self, form):
        form.instance.author = self.request.user  # 初始化表单数据
        # print(form.cleaned_data)
        return super(CreateView, self).form_valid(form)


# 修改文章 blog/update/<id>/<slug>
@method_decorator(login_required, name='dispatch')
class ArticleUpdateView(Common, UpdateView):
    '''修改文章'''

    def get_object(self, queryset=None): 
        obj = Article.objects.get(id=self.kwargs['id'], slug=self.kwargs['slug']) 
        return obj

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['is_updata'] = '修改文章'
        return context

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            self.success_url = self.object.get_absolute_url()  # 成功后跳转地址
        return super(UpdateView, self).form_valid(form)


# 删除文章
@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('app_blog.delete_article', 'app_blog:article_list'), name='dispatch')  # 此页面需要验证权限
class ArticleDeleteView(DeleteView):
    '''删除文章'''
    queryset = Article.objects.all()
    success_url = reverse_lazy('app_admin:blog_list')
    template_name = 'app_admin/blog/article_confirm_delete.html'


    def post(self, request, *args, **kwargs):
        print(50*'%')
        id = self.request.POST.get('id')
        slug = self.request.POST.get('slug')
        if id and slug:
            try:
                a = Article.objects.filter(pk=int(id), slug=slug, is_delete=False).update(is_delete=True)  # 返回已更新条目的数量
                if a==0:
                    data = {'status':500,'info':'找不到对应的Article'}
                else: data = {'status':200,'info':'success'}
            except:
                data = {'status':500,'info':'找不到对应的Article'}
        else:
            data = {'status':400,'info':'数据不完整'}
        return JsonResponse(data)



# 发表文章
@login_required()
def article_publish(request, pk, slug1):
    '''发表文章'''
    article = get_object_or_404(Article, pk=pk, author=request.user)
    article.to_publish()
    return redirect(reverse("app_blog:article_detail", args=[str(pk), slug1]))




# user_manage/
@method_decorator(superuser_only('app_user:login'), name='dispatch')  # dispatch 表示所有请求，因为所有请求都先经过dispatch
class AdminUserListView(ListView):
    '''用户列表'''
    paginate_by = 10
    template_name = 'app_admin/user/admin_user.html'

    def get_queryset(self):
        return User.objects.all()

    def get_context_data(self, **kwargs):
        username = ''
        fields = ['id','last_login','is_superuser','username','email','date_joined','is_active','first_name']
        if username == '':
            user_data = User.objects.all().values_list(*fields)
        else:
            user_data = User.objects.filter(username__icontains=username).values_list(*fields)

        table_data = [dict(zip(fields, i)) for i in user_data]
        context = super().get_context_data(**kwargs)
        context['table_data'] = table_data
        return context

