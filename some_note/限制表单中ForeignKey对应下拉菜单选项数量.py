# 有文章 Article 和类别 Category 两个模型，其中类别和文章是一对多的关系。
# 我们希望某个用户在使用表单创建或编辑某篇新文章时，
# 表单上类别对应的下拉菜单选项不显示所有类别，
# 而只显示用户自己创建的类别。


# forms.py
from django import forms
from app_blog.models import Article, Category
class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        exclude = ['author',]


# views.py
# 1.类视图
# 我们可以在视图里对表单ForeignKey对应下拉菜单选项的内容和数量做出限制。
# 通过重写基于类的视图自带的 get_context_data 方法，你可以对 form 的任何字段做出修改和限制。
# 比如本例中限定了category 对应的 queryset 仅限于用户自己创建的类别。
from django.views.generic.edit import CreateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
@method_decorator(login_required, name='dispatch')
class ArticleCreateView(CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'app_blog/article_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 修改 form 字段
        context['form'].fields['category'].queryset = Category.objects.filter(author=self.request.user)
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

# 2.函数视图
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
@login_required
def article_create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user  # Set the user object here
            article.save()  # Now you can send it to DB
            return redirect("/blog/")
    else:
        form = ArticleForm()
        # 修改 form 字段
        form.fields['category'].queryset = Category.objects.filter(author=request.user)
    return render(request, 'blog/article_create_form.html', {'form': form, })

# 注意：
# 本例ArticleForm使用的是ModelForm，由模型创建，所以使用form.fields['category']获取category字段。
# 如果你是自定义的普通form，应使用form.category获取category字段