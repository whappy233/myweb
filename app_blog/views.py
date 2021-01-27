from app_comments.forms import CommentForm
from django import forms
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.core import paginator
from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator  # 分页
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views.generic import DetailView, ListView
from loguru import logger
from taggit.models import Tag  # 导入标签模型
from myweb.utils import cache
from .forms import EmailArticleForm, SearchForm
from .models import Article, Category


class ArticleListView(ListView):
    template_name = 'blog/article_list.html'  # 视图默认的模板名称是: 模型名小写_list.html
    context_object_name = 'article_list'  # 设置上下文变量

    page_type = ''
    paginate_by = 5  # 每页obj的数目 生成 page_obj 对象
    page_kwarg = 'page'  # get 请求页码的参数 /?page=2

    def get_view_cache_key(self):
        return self.request.get['page']  # 当前页码

    @property
    def page_number(self):
        '''返回当前请求的页码'''
        page_kwarg = self.page_kwarg
        page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
        return page

    def get_queryset_cache_key(self):
        """ 子类重写.获得queryset的缓存key """
        raise NotImplementedError()

    def get_queryset_data(self):
        """ 子类重写.获取queryset的数据 """
        raise NotImplementedError()

    def get_queryset_from_cache(self, cache_key):
        """ 缓存页面数据 """ 
        value = cache.get(cache_key)
        if value:
            logger.info(f'获取视图缓存, KEY: {cache_key}')
            return value
        else:
            article_list = self.get_queryset_data()
            cache.set(cache_key, article_list)
            logger.info(f'设置视图缓存, KEY: {cache_key}')
            return article_list

    def get_queryset(self):
        """ 从缓存获取数据 """
        key = self.get_queryset_cache_key()
        value = self.get_queryset_from_cache(key)
        return value

    def get_context_data(self, **kwargs):
        context = super(ArticleListView, self).get_context_data(**kwargs)
        context['section'] = 'blog'
        context['form'] = SearchForm()
        return context

# 文章列表
@method_decorator(logger.catch(), name='dispatch')
class IndexView(ArticleListView):

    def get_queryset_data(self):
        article_list = Article.published.all()
        return article_list

    def get_queryset_cache_key(self):
        cache_key = f'{__class__.__name__}_{self.page_number}'
        return cache_key

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        return context

# 某个标签下的文章
class TagDetailView(ArticleListView):
    page_type = '分类标签归档'

    def get_queryset_data(self):
        tag_slug = self.kwargs.get('tag_slug')
        tag = get_object_or_404(Tag, slug=tag_slug)
        self.name = tag_name = tag.name
        article_list = Article.published.filter(tags__name=tag_name)
        return article_list

    def get_queryset_cache_key(self):
        tag_slug = self.kwargs.get('tag_slug')
        tag = get_object_or_404(Tag, slug=tag_slug)
        self.name = tag_name = tag.name
        cache_key = f'{__class__.__name__}_{tag_name}_{self.page_number}'
        return cache_key

    def get_context_data(self, **kwargs):
        context = super(TagDetailView, self).get_context_data(**kwargs)
        context['page_type'] = AuthorDetailView.page_type
        context['tag_name'] = self.name
        return context

# 某个作者下的文章
class AuthorDetailView(ArticleListView):
    page_type = '作者文章归档'

    def get_queryset_cache_key(self):
        author_name = self.kwargs['author_name']
        cache_key = f'{__class__.__name__}_{author_name}_{self.page_number}'
        return cache_key

    def get_queryset_data(self):
        author_name = self.kwargs['author_name']
        article_list = Article.published.filter(author__username=author_name)
        return article_list

    def get_context_data(self, **kwargs):
        context = super(AuthorDetailView, self).get_context_data(**kwargs)
        context['page_type'] = AuthorDetailView.page_type
        context['tag_name'] = self.kwargs['author_name']
        return context

# 某个分类下的文章
class CategoryDetailView(ArticleListView):

    page_type = "分类目录归档"

    def get_queryset_data(self):
        slug = self.kwargs['category_slug']
        category = get_object_or_404(Category, slug=slug)
        self.category_name = category.name

        # category_names = list(map(lambda c: c.name, category.get_sub_categorys()))
        # article_list = Article.published.filter(category__name__in=category_names)

        a = '|'.join(f'Q(category={i.id})' for i in category.get_sub_categorys())
        article_list = Article.published.filter(eval(a))

        return article_list

    def get_queryset_cache_key(self):
        slug = self.kwargs['category_slug']
        category = get_object_or_404(Category, slug=slug)
        self.category_name = category.name
        cache_key = f'{__class__.__name__}_{self.category_name}_{self.page_number}'
        return cache_key

    def get_context_data(self, **kwargs):
        context = super(CategoryDetailView, self).get_context_data(**kwargs)
        context['page_type'] = CategoryDetailView.page_type
        context['tag_name'] = self.category_name
        return context


# 文章详情
class ArticleDetailView(DetailView):
    '''文章详细'''
    model = Article

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        comment_form = CommentForm()
        user = self.request.user
        if user.is_authenticated and not user.is_anonymous and user.email and user.username:
            comment_form.fields.update({
                'email': forms.CharField(widget=forms.HiddenInput()),
                'name': forms.CharField(widget=forms.HiddenInput()),
            })
            comment_form.fields["email"].initial = user.email
            comment_form.fields["name"].initial = user.username

        comments = self.object.comment_list()
        context.update({
            'comments': comments,
            'comment_form': comment_form,
            'section': 'blog',
        })

        return context

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        obj.viewed()
        self.object = obj
        return obj


# 文章列表 (类视图) Old
@method_decorator(logger.catch(), name='dispatch')
class ArticleListView_old(ListView):
    # context_object_name = 'page_obj'  # 设置上下文变量
    paginate_by = 3  # 3个一页 生成 page_obj 对象
    # template_name = 'app_blog/article_list.html'  # 视图默认的模板名称是: 模型名小写_list.html

    def get_queryset(self):
        self.tag__ = self.author_name__ = self.search_keyword = None
        obj = Article.published.all()
        tag_slug = self.kwargs.get('tag_slug')
        self.author_name__ = author_name = self.kwargs.get('author_name')
        self.search_keyword = keyword = self.request.GET.get('keyword', None)

        if tag_slug:
            self.tag__ = tag = get_object_or_404(Tag, slug=tag_slug)
            obj = obj.filter(tags__in=[tag])
        if author_name:
            obj = obj.filter(author__username=author_name)
        if keyword:
            obj = obj.filter(Q(title__icontains=keyword)|Q(body__icontains=keyword))

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SearchForm()
        context['section'] = 'blog'
        context['tag'] = self.tag__
        context['name'] = self.author_name__
        context['keyword'] = self.search_keyword
        return context


# 月度归档(某月的列表)
def month_archive(request, year, month):
    '''月度归档'''
    articles = Article.published.filter(publish__year=year, publish__month=month).order_by('-publish')
    paginator = Paginator(articles, 3)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    context = {
        'page_obj': page_obj, 
        'paginator': paginator, 
        'is_paginated': True, 
        'year_month': (year, month)}
    return render(request, 'app_blog/month_archive.html', context)


# 所有文章 (函数视图)
@login_required
def article_list(request, tag_slug=None, author_name=None):
    object_list = Article.published.all()  # 自定义的管理器published(只显示published 的文章)
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])
    if author_name:
        user = get_object_or_404(User, username=author_name)  # 1  方式1
        object_list = object_list.filter(author=user)  # 1
        # object_list = Article.published.filter(author__username=author_name)   # 2  方式2

    paginator = Paginator(object_list, 3)
    page = request.GET.get('page')
    # articles = paginator.get_page(page)
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:  # 非整数
        articles = paginator.page(1)
    except EmptyPage:  # 页码不存在, 返回当前页
        if int(page) > paginator.num_pages:  # 返回尾页
            # paginator.num_pages 页面数
            articles = paginator.page(paginator.num_pages)
        else:
            articles = paginator.page(1)

    context = {
        'page_obj': articles,
        'tag': tag,
        'name': author_name,
        'section': 'blog'
    }

    return render(request, 'app_blog/article_list.html', context)


# 点👍 +1
# @login_required
@require_http_methods(["POST"])  # 只接受 POST 方法
def blog_like(request):
    blog_id = request.POST.get('id')
    action = request.POST.get('action')
    if blog_id and action:
        try:
            blog = Article.published.get(id=blog_id)
            if action == 'like':
                blog.users_like.add(request.user)
            else:
                blog.users_like.remove(request.user)
            count = blog.users_like.count()
            return JsonResponse({'status':'ok', 'count': count})
        except Exception as e:
            print(e)
            logger.error('')
            pass
    return JsonResponse({'status':'fail'})


# From 表单 (分享文章)
@login_required
def article_share(request, article_id):
    article = get_object_or_404(Article, id=article_id, status='p')  # 检索ID
    sent = False
    if request.method == 'POST':
        form = EmailArticleForm(data=request.POST)  # 提交表单
        # print(form.errors)  # 错误列表
        if form.is_valid():  # 判断数据是否合法
            cd = form.cleaned_data  # 表单字段及对应值的字典( 若表单字段未被验证，则只包含有效的字段 )
            # 发邮件
            # build_absolute_uri
            # 假设当前路径为:127.0.0.1/123/456/7
            # article.get_absolute_url() 路径为: 456/789/6
            # 那么article_url 路径为 127.0.0.1/123/456/789/6
            article_url = request.build_absolute_uri(article.get_absolute_url())
            subject = f"{cd['name']}({cd['email']}) 分享给你 '{article.title}'"
            message = f"Read '{article.title}' at {article_url} \n\n{cd['name']}\'s comments:{cd['comments']}"
            # send_mail(subject, message, 'haha@qq.com', [cd['to']])
            sent = True
    else:
        form = EmailArticleForm()

    context = {
        'article': article,
        'form': form,
        'sent': sent,
        'section': 'blog'
    }
    return render(request, 'app_blog/share.html', context)


# 搜索实时反馈
def ajax_search(request):
    count = 0
    if request.method == 'GET':
        keyword = request.GET.get('keyword', None)
        if keyword:
            count = Article.published.filter(Q(title__icontains=keyword)|Q(body__icontains=keyword)).count()
    return JsonResponse({'count': count, })


# ajax 测试
def ajax_test(request):
    if request.method == 'GET':
        keyword = request.GET.get('keyword', None)
        print(keyword)
        if keyword:
            data = {'count': f'Carlos-{timezone.now()}', }
            return JsonResponse(data)
