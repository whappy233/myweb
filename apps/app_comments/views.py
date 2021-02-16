
from django import forms
from django.apps import apps
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.http.response import Http404
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.edit import FormView
from loguru import logger
from .forms import CommentForm




class CommentPostView(FormView):
    form_class = CommentForm
    template_name = 'app_blog/article_detail.html' # get 请求返回

    def get(self, request, *args, **kwargs):
        article_id = self.kwargs['article_id']

        model_class = apps.get_model('app_blog', 'article')

        article = get_object_or_404(model_class, id=article_id)
        url = article.get_absolute_url()
        return redirect(url + "#comments")

    def form_invalid(self, form):
        '''如果表单无效，则呈现无效表单'''
        article_id = self.kwargs['article_id']

        model_class = apps.get_model('app_blog', 'article')

        article = model_class.objects.get(pk=article_id)
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

        model_class = apps.get_model('app_blog', 'article')

        article = model_class.objects.get(pk=article_id)
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

    if request.method == 'POST':
        # <QueryDict: {
        # 'comment_id': ['9'], 
        # 'obj_id': ['9'], 
        # 'csrfmiddlewaretoken': ['b1km5IExy4nQUZzQul2mGiAFQzThh6OvkRYn8fKeK6TUB6DwCRiryiPwbbbMZpab']}>
        comment_id = request.POST.get('comment_id')
        obj_id = request.POST.get('obj_id')
        try:
            model_class = apps.get_model('app_blog', 'article')

            article = model_class.objects.get(pk=obj_id)
            commnet = article.comments.get(pk=comment_id)
            commnet.delete()
            return JsonResponse({'status':200})
        except Exception as e:
            print(e)
        return JsonResponse({'status':500})
    logger.error('不允许GET请求!')
    raise Http404()
