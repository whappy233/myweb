from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger  # 分页
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Post, Comment, Category
from django.http import HttpResponse, JsonResponse, Http404
from .forms import EmailPostForm, CommentForm, SearchForm, PostForm
from django.core.mail import send_mail
from taggit.models import Tag  # 导入标签模型
from django.db.models import Count, Q
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity


# from django.template import loader
# def index(request):
#     latest_question_list = Comment.objects.order_by('-pub_date')[:5]
#     template = loader.get_template('polls/index.html')
#     context = {
#         'latest_question_list': latest_question_list,
#     }
#     return HttpResponse(template.render(context, request))


# 类视图
# 所有文章
# django 中的通用视图 ListView 将所选页面传递到变量 page_obj 中
# path('', views.PostListView.as_view(), name='post_list')
class PostListView(ListView):
    queryset = Post.published.all()  # === model = Post
    # model = Post
    # context_object_name = 'page_obj'  # 设置上下文变量
    paginate_by = 3  # 3个一页
    template_name = 'app_blog/list.html'  # 使用自定义模板渲染

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'blog'
        return context


# 函数视图
@login_required
def post_list(request, tag_slug=None, author_name=None):
    object_list = Post.published.all()  # 自定义的管理器published(只显示published 的文章)
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])
    if author_name:
        user = get_object_or_404(User, username=author_name)  # 1  方式1
        object_list = object_list.filter(author=user)  # 1
        # object_list = Post.published.filter(author__username=author_name)   # 2  方式2

    paginator = Paginator(object_list, 3)
    page = request.GET.get('page')
    # posts = paginator.get_page(page)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:  # 非整数
        posts = paginator.page(1)
    except EmptyPage:  # 页码不存在, 返回当前页
        if int(page) > paginator.num_pages:  # 返回尾页
            # paginator.num_pages 页面数
            posts = paginator.page(paginator.num_pages)
        else:
            posts = paginator.page(1)

    context = {
        'page_obj': posts,
        'tag': tag,
        'name': author_name,
        'section': 'blog'
    }

    return render(request, 'app_blog/list.html', context)

# 文章详情
# path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.post_detail, name='post_detail')
@login_required
def post_detail(request, year, month, day, post):
    # 使用 get() 返回一个对象，如果该对象不存在，则引发Http404异常。
    post = get_object_or_404(Post,
                             slug=post,
                             status='p',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day,
                             )

    post.viewed()  # 阅读量 +1

    comments = post.comments.filter(active=True)  # 查询所有评论
    message = ''

    has_commented = request.session.get('has_commented', False)
    if not has_commented:
        if request.method == 'POST' and not has_commented:
            comment_form = CommentForm(data=request.POST)  # 提交表单
            if comment_form.is_valid():
                # 创建表单连接的模型实例(commit=False, 不会立即保存到数据库中),save()方法仅适用于ModelsForm
                new_comment = comment_form.save(commit=False)
                new_comment.post = post
                new_comment.save()
                request.session['has_commented'] = True
                return redirect(post.get_absolute_url())
    else:
        message = '你已经评论过了'

    comment_form = CommentForm()

    # 相似文章
    post_tags_ids = post.tags.values_list('id', flat=True)  # 当前帖子的 Tag ID 列表

    # qq = '|'.join(['Q(tags=%s)' % i for i in list(post_tags_ids)])  # Q(tags=1)|Q(tags=2)...
    # similar_posts = Post.published.filter(eval(qq)).exclude(id=post.id)  # 获取所有此标签的全部帖子,排除自身

    # 获取包含此标签或分组的全部帖子,排除自身
    similar_posts = Post.published.filter(
        Q(tags__in=post_tags_ids) | Q(category=post.category)).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count(
        'tags'), some_category=Count('category')).order_by('-same_tags', '-publish')[:4]

    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'similar_posts': similar_posts,
        'section': 'blog',
        'message': message,
    }

    return render(request, 'app_blog/detail.html', context)




# 文章列表 - PostListView - 不需要login_required装饰器
# 文章详情 - PostDetailView - 不需要login_required装饰器
# 创建文章 - PostCreateView - 需要login_required装饰器
# 修改文章 - PostUpdateView - 需要login_required装饰器
# 删除文章 - PostDeleteView - 需要login_required装饰器
# 查看已发布文章 - PublishedPostListView - 需要login_required装饰器
# 草稿箱 - PostDraftListView - 需要login_required装饰器
# 发表文章 (由草稿变发布) - 需要login_required装饰器


# Create your views here.
class PostListView1(ListView):
    paginate_by = 3

    def get_queryset(self):
        return Post.objects.filter(status='p').order_by('-pub_date')

# 已发布文章列表
@method_decorator(login_required, name='dispatch')
class PublishedPostListView(ListView):
    '''已发布文章列表'''
    template_name = "blog/published_article_list.html"
    paginate_by = 3

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user).filter(status='p').order_by('-pub_date')

@method_decorator(login_required, name='dispatch')
class PostDraftListView(ListView):
    template_name = "app_blog/article_draft_list.html"
    paginate_by = 3

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user).filter(status='d').order_by('-pub_date')

# 文章详细
class PostDetailView(DetailView):
    '''文章详细'''
    model = Post

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        obj.viewed()
        return obj

# 创建文章
@method_decorator(login_required, name='dispatch')
class PostCreateView(CreateView):
    '''创建文章'''
    model = Post
    form_class = PostForm
    template_name = 'app_blog/article_create_form.html'

    # Associate form.instance.user with self.request.user
    def form_valid(self, form):

        form.instance.author = self.request.user
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'app_blog/article_update_form.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if obj.author != self.request.user:
            raise Http404()
        return obj

@method_decorator(login_required, name='dispatch')
class PostDeleteView(DeleteView):
    model = Post
    success_url = reverse_lazy('app_blog:article_list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if obj.author != self.request.user:
            raise Http404()
        return obj

# 文章详情
@login_required()
def article_publish(request, pk, slug1):
    '''文章详情'''
    article = get_object_or_404(Post, pk=pk, author=request.user)
    article.published()
    return redirect(reverse("app_blog:article_detail", args=[str(pk), slug1]))





# From 表单 (分享文章)
@login_required
def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='p')  # 检索ID
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(data=request.POST)  # 提交表单
        # print(form.errors)  # 错误列表
        if form.is_valid():  # 判断数据是否合法
            cd = form.cleaned_data  # 表单字段及对应值的字典( 若表单字段未被验证，则只包含有效的字段 )
            # 发邮件
            # build_absolute_uri
            # 假设当前路径为:127.0.0.1/123/456/7
            # post.get_absolute_url() 路径为: 456/789/6
            # 那么post_url 路径为 127.0.0.1/123/456/789/6
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']}({cd['email']}) 分享给你 '{post.title}'"
            message = f"Read '{post.title}' at {post_url} \n\n{cd['name']}\'s comments:{cd['comments']}"
            # send_mail(subject, message, 'haha@qq.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()

    context = {
        'post': post,
        'form': form,
        'sent': sent,
        'section': 'blog'
    }
    return render(request, 'app_blog/share.html', context)

# Search
def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            # 普通搜索排序
            # results = Post.objects.annotate(search=SearchVector('title', 'body')).filter(search=query)
            # ------------------------------------------------------------------------------------------
            # 搜索相关性排序
            # search_vector = SearchVector('title', 'body')
            # search_query = SearchQuery(query)
            # results = Post.objects.annotate(search=search_vector, rank=SearchRank(search_vector, search_query)
            #                                 ).filter(search=search_query).order_by('-rank')
            # ------------------------------------------------------------------------------------------
            # 加权查询
            # A,B,C,D权值分别为1.0, 0.4, 0.2, 0.1
            # title 使用权值A:1.0, body 使用权值B:0.4
            # search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
            # search_query = SearchQuery(query)
            # rank__gte=0.3 : 仅显示大于0.3 的结果
            # results = Post.objects.annotate(rank=SearchRank(search_vector, search_query)
            #                                 ).filter(rank__gte=0.3).order_by('-rank')
            # ------------------------------------------------------------------------------------------
            # 三元搜索
            results = Post.objects.annotate(similarity=TrigramSimilarity('title', query),
                                            ).filter(similarity__gt=0.3).order_by('-similarity')

    context = {
        'form': form,
        'query': query,
        'results': results,
        'section': 'blog'
    }
    return render(request, 'app_blog/search.html', context)

# ajax 测试
def ajax_test(request):
    if request.method == 'GET':
        keyword = request.GET.get('keyword', None)
        print(keyword)
        if keyword:
            data = {'count': f'Carlos-{timezone.now()}', }
            return JsonResponse(data)
