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

from .forms import ArticleCreateForm

from app_blog.models import Article, Category, Comment
from app_user.models import UserProfile


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


# 所有文章列表
# blog/
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
    success_url = reverse_lazy('app_admin:blog_list')  # 成功后跳转地址

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

