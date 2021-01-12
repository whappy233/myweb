from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User

from django.core import paginator
from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator  # 分页
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from taggit.models import Tag  # 导入标签模型

from .forms import CommentForm, EmailArticleForm, SearchForm
from .models import Article, Category, Comment


# 所有文章 (类视图)
class ArticleListView(ListView):
    # context_object_name = 'page_obj'  # 设置上下文变量
    paginate_by = 3  # 3个一页 生成 page_obj 对象
    # template_name = 'app_blog/article_list.html'  # 视图默认的模板名称是: 模型名小写_list.html

    def get_queryset(self):
        self.tag__ = None
        obj = Article.published.all()
        tag_slug = self.kwargs.get('tag_slug')
        self.author_name__ = author_name = self.kwargs.get('author_name')
        keyword = self.request.GET.get('keyword', None)

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
        return context


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


# 文章详情
class ArticleDetailView(DetailView):
    '''文章详细'''
    model = Article

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        message = ''
        comments = self.object.comments.filter(active=True)  # 查询所有评论
        # 相似文章
        article_tags_ids = self.object.tags.values_list('id', flat=True)  # 当前帖子的 Tag ID 列表
        # 获取包含此标签或分组的全部帖子,排除自身
        similar_articles = Article.published.filter(Q(tags__in=article_tags_ids) | Q(category=self.object.category)).exclude(id=self.object.id)
        similar_articles = similar_articles.annotate(same_tags=Count('tags'), some_category=Count('category')).order_by('-same_tags', '-publish')[:4]

        comment_form = CommentForm()

        context.update({
            'comments': comments,
            'comment_form': comment_form,
            'similar_articles': similar_articles,
            'section': 'blog',
            'message': message,
        })

        return context

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        obj.viewed()
        return obj

    def post(self, request, *args, **kwargs):
        message = ''
        self.object = article = self.get_object()
        has_commented = request.session.get('has_commented', False)
        if not has_commented:
            comment_form = CommentForm(data=request.POST)  # 提交表单
            if comment_form.is_valid():
                # 创建表单连接的模型实例(commit=False, 不会立即保存到数据库中),save()方法仅适用于ModelsForm
                new_comment = comment_form.save(commit=False)
                new_comment.article = article
                new_comment.save()
                request.session['has_commented'] = True
                return redirect(article.get_absolute_url())
        else:
            message = '你已经评论过了'

        context = self.get_context_data()
        context.update({'message': message,})

        return render(request, 'app_blog/article_detail.html', context)


# 分组下的文章列表
class CategoryDetailView(DetailView):
    '''分组下的文章列表'''
    model = Category

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.object.has_child():
            articles = Article.objects.filter()
            categories = self.object.category_set.all()  # 所有子类目
            for category in categories:
                queryset = Article.objects.filter(category=category.id).order_by('-publish')
                articles.union(queryset)
        else:
            articles = Article.objects.filter(category=self.object.id).order_by('-publish')

        paginator = Paginator(articles, 3)
        page = self.request.GET.get('page')
        page_obj = paginator.get_page(page)
        context['page_obj'] = page_obj
        context['is_paginated'] = True
        context['section'] = 'blog'
        return context


# 月度归档(某月的列表)
def month_archive(request, year, month):
    '''月度归档'''
    articles = Article.objects.filter(status='p', publish__year=year, publish__month=month).order_by('-publish')
    paginator = Paginator(articles, 3)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    
    context = {'page_obj': page_obj, 'paginator': paginator, 'is_paginated': True, 'year_month': (year, month)}
    return render(request, 'app_blog/month_archive.html', context)


# 点👍 +1
@login_required
@require_http_methods(["POST"])  # 只接受 POST 方法
def blog_like(request):
    blog_id = request.POST.get('id')
    action = request.POST.get('action')
    print(blog_id)
    print(action)
    if blog_id and action:
        try:
            blog = Article.objects.get(id=blog_id)
            if action == 'like':
                blog.users_like.add(request.user)
            else:
                blog.users_like.remove(request.user)
            count = blog.users_like.count()
            return JsonResponse({'status':'ok', 'count': count})
        except:
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
