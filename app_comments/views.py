from django.shortcuts import render
from django import forms
from django.views.generic.edit import FormView
from app_comments.forms import CommentForm
from app_blog.models import Article
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import get_user_model



class CommentPostView(FormView):
    form_class = CommentForm
    template_name = 'app_blog/article_detail.html' # get 请求返回

    def get(self, request, *args, **kwargs):
        article_id = self.kwargs['article_id']
        article = get_object_or_404(Article, id=article_id)
        url = article.get_absolute_url()
        return redirect(url + "#comments")

    def form_invalid(self, form):
        '''如果表单无效，则呈现无效表单'''
        article_id = self.kwargs['article_id']
        article = Article.objects.get(pk=article_id)
        user = self.request.user
        if user.is_authenticated:
            form.fields.update({
                'email': forms.CharField(widget=forms.HiddenInput()),
                'name': forms.CharField(widget=forms.HiddenInput()),
            })
            form.fields["email"].initial = user.email
            form.fields["name"].initial = user.username

        return self.render_to_response({
            'comment_form': form,
            'article': article
        })

    def form_valid(self, form):
        """提交的数据验证合法后的逻辑"""
        article_id = self.kwargs['article_id']
        article = Article.objects.get(pk=article_id)
        has_commented = self.request.session.get('has_commented', None)
        if (not has_commented) or (has_commented!=article_id):

            user = self.request.user
            if not user.is_authenticated:
                email = form.cleaned_data['email']
                username = form.cleaned_data['name']
                user = get_user_model().objects.get_or_create(username=username, email=email)[0]
                # auth.login(self.request, user)
            comment = form.save(False)
            comment.content_object = article
            comment.author = user
            comment.save(True)
            # self.request.session['has_commented'] = article.id
            # self.request.session.set_expiry(300)
            return redirect("%s#div-comment-%d" %(article.get_absolute_url(), comment.pk))

        else:
            message = '你已经评论过了, 五分钟后可再次评论.'
            print(message)
            url = article.get_absolute_url()
            return redirect(url + "#comments_你已经评论过了, 五分钟后可再次评论")



def ajax_delete_comment(request):
    pass