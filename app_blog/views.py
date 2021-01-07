from django.core import paginator
from django.http.request import HttpRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger  # 分页
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, permission_required
from django.utils import timezone
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

# 类视图
# 所有文章
# django 中的通用视图 ListView 将所选页面传递到变量 page_obj 中
# path('', views.PostListView.as_view(), name='post_list')
class PostListView(ListView):
    queryset = Post.published.all()  # === model = Post
    # model = Post
    # context_object_name = 'page_obj'  # 设置上下文变量
    paginate_by = 3  # 3个一页 生成 page_obj 对象
    # template_name = 'app_blog/post_list.html'  # 视图默认的模板名称是: 模型名小写_list.html

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

    return render(request, 'app_blog/post_list.html', context)

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

# 分组下的文章列表
class CategoryDetailView(DetailView):
    '''分组下的文章列表'''
    model = Category

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.object.has_child():
            posts = Post.objects.filter()
            categories = self.object.category_set.all()  # 所有子类目
            for category in categories:
                queryset = Post.objects.filter(category=category.id).order_by('-publish')
                posts.union(queryset)
        else:
            posts = Post.objects.filter(category=self.object.id).order_by('-publish')

        paginator = Paginator(posts, 3)
        page = self.request.GET.get('page')
        page_obj = paginator.get_page(page)
        context['page_obj'] = page_obj
        context['is_paginated'] = True
        context['section'] = 'blog'
        return context


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
            blog = Post.objects.get(id=blog_id)
            if action == 'like':
                blog.users_like.add(request.user)
            else:
                blog.users_like.remove(request.user)
            count = blog.users_like.count()
            return JsonResponse({'status':'ok', 'count': count})
        except:
            pass
    return JsonResponse({'status':'fail'})


# 文章详细
class PostDetailView(DetailView):
    '''文章详细'''
    model = Post

    # def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
    #     context = super().get_context_data(**kwargs)
    #     comments = post.comments.filter(active=True)  # 查询所有评论

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        obj.viewed()
        return obj



# Admin -------------------------------------------------

# 所有文章列表
# post/admin/
# 权限名一般由app名(app_label)，权限动作和模型名组成。以 app_blog 应用为例，Django为 Post 模型自动创建的4个可选权限名分别为:
# 查看文章(view): app_blog.view_post
# 创建文章(add): app_blog.add_post
# 更改文章(change): app_blog.change_post
# 删除文章(delete): app_blog.delete_post
# 在视图中可以使用 user.has_perm() 方法来判断一个用户是不是有相应的权限, 
# user_A.has_perm('app_blog.add_post')
# user_A.has_perm('app_blog.change_post)

# 最快捷的方式是使用 @permission_required 这个装饰器
# permission_required(perm, login_url=None, raise_exception=False)
# raise_exception=True, 会直接返回403无权限的错误
# 没有权限将会跳转到 login_url='app_blog:post_list'

# 如果你使用基于类的视图(Class Based View), 可以继承PermissionRequiredMixin这个类
# from django.contrib.auth.mixins import PermissionRequiredMixin
# class MyView(PermissionRequiredMixin, View):
    # permission_required = 'polls.can_vote'
    # Or multiple of permissions:
    # permission_required = ('polls.can_open', 'polls.can_edit')

@method_decorator(login_required, name='dispatch')  # 此页面需要登录
@method_decorator(permission_required('app_blog.delete_post', 'app_blog:post_list'), name='dispatch')  # 此页面需要验证权限
class AdminPostListView(ListView):
    '''文章列表'''
    paginate_by = 10
    template_name = 'admin/post_list.html'

    # def get(self, request, *args, **kwargs):

    #     show_publish = self.request.GET.get('draft')
    #     if show_publish:
    #         posts = Post.objects.filter(status='p').order_by('-publish')
    #     else:
    #         posts = Post.objects.filter(status='d').order_by('-publish')
    #     paginator = Paginator(posts, 5)
    #     page = self.request.GET.get('page')
    #     page_obj = paginator.get_page(page)
    #     context = {
    #         'page_obj': page_obj,
    #         'show_publish': show_publish
    #     }
        # return render(request, 'admin/post_list.html', context)

    def get_queryset(self):
            return Post.objects.all().order_by('-publish')


# 创建文章
# blog/create/
@method_decorator(login_required, name='dispatch')
class PostCreateView(CreateView):
    '''创建文章'''
    model = Post
    form_class = PostForm
    template_name = 'admin/blog_create.html'
    success_url = reverse_lazy('app_blog:admin_post_list')  # 成功后跳转地址

    # Associate form.instance.user with self.request.user
    def form_valid(self, form):
        form.instance.author = self.request.user
        # print(form.cleaned_data)
        return super().form_valid(form)


# 修改文章
@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    '''修改文章'''
    model = Post
    form_class = PostForm
    template_name = 'app_blog/blog_update_form.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if obj.author != self.request.user:
            raise Http404()
        return obj

# 删除文章
@method_decorator(login_required, name='dispatch')
class PostDeleteView(DeleteView):
    '''删除文章'''
    model = Post
    success_url = reverse_lazy('app_blog:post_list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if obj.author != self.request.user:
            raise Http404()
        return obj

# 发表文章
@login_required()
def post_publish(request, pk, slug1):
    '''发表文章'''
    post = get_object_or_404(Post, pk=pk, author=request.user)
    post.to_publish()
    return redirect(reverse("app_blog:post_detail", args=[str(pk), slug1]))



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
