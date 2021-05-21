
from app_blog.models import Article
from app_user.utils import validateEmail
from django import forms
from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.forms.models import modelform_factory
from django.forms.utils import ErrorDict
from django.http import JsonResponse, QueryDict, request
from django.http.response import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic.base import View
from django.views.generic.edit import FormView
from loguru import logger

from .forms import CommentForm
from .models import Comments, Wanderer

# model_class = apps.get_model('app_blog', 'article')



# 增加评论 old
class CommentPostView(FormView):
    form_class = CommentForm
    template_name = 'tp/文章详情.html' # get 请求返回

    def get(self, request, *args, **kwargs):
        article_slug = self.kwargs['article_slug']

        article = get_object_or_404(Article, slug=article_slug)
        url = article.get_absolute_url()
        print(20*'*')
        return redirect(url + "#comments")

    def form_invalid(self, form):
        '''如果表单无效，则呈现无效表单'''
        article_slug = self.kwargs['article_slug']

        article = get_object_or_404(Article, slug=article_slug)
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
            'article': article,
            'comments': article.comment_list()
        })

    def form_valid(self, form):
        """表单验证成功后的逻辑"""
        article_slug = self.kwargs['article_slug']

        article = get_object_or_404(Article, slug=article_slug)
        has_commented = self.request.session.get('has_commented', None)
        if (not has_commented) or (has_commented!=article_slug):

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




class CommentsView(View):

    def get(self, request, *args, **kwargs):
        return HttpResponse('评论系统')

    # 增加评论
    def post(self, request, *args, **kwargs):
        if request.is_ajax:   

            article_slug = request.POST.get('object_slug', '')
            comment_body = request.POST.get('comment_body', '')

            replyto = request.POST.get('replyto', '')

            username = request.POST.get('username', '')
            nickname = request.POST.get('nickname', '')
            email = request.POST.get('email', '')

            print(len(str(email)))

            if article_slug and comment_body:
                try:
                    article = Article.objects.get(slug=article_slug)
                except:
                    return JsonResponse({'status': 404, 'msg':'数据获取失败'})

                if request.user.is_authenticated and request.user.username==username:
                    wanderer = None
                    author = request.user
                elif username and not (nickname and email):
                    return JsonResponse({'status': 402, 'msg':'页面过期请刷新页面'}) 
                else:
                    if not 0 < len(str(nickname)) < 20:
                        return JsonResponse({'status': 401, 'msg':'请求数据非法(nickname 控制在20字以内)'}) 
                    if not 0 < len(str(email)) < 50:
                        return JsonResponse({'status': 401, 'msg':'请求数据非法(email 控制在50字以内)'}) 
                    if not validateEmail(email):
                        return JsonResponse({'status': 401, 'msg':'请求数据非法(Email 格式错误)'}) 
                    if Wanderer.objects.filter(email=email).exists():
                        return JsonResponse({'status': 401, 'msg':'Email 已存在'})
                    try:
                        wanderer = Wanderer.objects.create(username=nickname, email=email)
                        author = None
                    except Exception as e:
                        return JsonResponse({'status': 401, 'msg':e})
                if replyto:
                    try:
                        parent_comment = Comments.objects.get(uuid=replyto)
                    except:
                        return JsonResponse({'status': 401, 'msg':'请求数据非法(目标评论不存在)'})
                else:
                    parent_comment = None
                try:
                    comment = Comments.objects.create(body=comment_body, author=author, wanderer=wanderer, parent_comment=parent_comment, content_object=article)
                except Exception as e:
                    if wanderer:
                        wanderer.delete()
                    return JsonResponse({'status': 401, 'msg':e})
                return JsonResponse({'status': 200, 'msg':'ok'})
            else:
                return JsonResponse({'status': 401, 'msg':'请求数据非法'})
        else:
            return HttpResponseForbidden()

    # 置顶评论
    def patch(self, request, *args, **kwargs):
        '''
        接受的数据:
            {
                uid: comment 唯一id
                要修改的字段: 对应值
            }
        '''
        data = QueryDict(request.body)
        model_fields = [f.name for f in Comments._meta.fields]

        uuid = data.get('uid')
        if not uuid:
            return JsonResponse({'status':404, 'msg': 'uuid错误'})

        try:
            uuid = Comments._meta.get_field('uuid').to_python(uuid)
            obj = Comments.objects.get(uuid=uuid)
        except (models.DoesNotExist, ValidationError):
            return JsonResponse({'status':404, 'msg': 'uuid查询失败, 数据不存在'})

        fields = [f for f in data.keys() if f in model_fields]

        defaults = {
            "form": forms.ModelForm,
            "fields": fields,
            # "formfield_callback": self.formfield_for_dbfield,
        }
        form_class = modelform_factory(Comments, **defaults)
        form = form_class(instance=obj, data=data, files=request.FILES)

        result = {}
        if form.is_valid():
            try:
                print(form.data)
                form.save(commit=True)
                result['result'] = 'success'
            except Exception as e:
                result['errors'] = str(e)
        else:
            result['result'] = 'error'
            result['errors'] = ErrorDict(form.errors).as_json()

        return JsonResponse(result)

    # 删除评论
    def delete(self, request, *args, **kwargs):
        data = QueryDict(request.body)
        uuid = data.get('uid')
        if not uuid:
            return JsonResponse({'status':401, 'msg': 'uuid 不存在'})

        try:
            comment = Comments.objects.get(uuid=uuid)
            comment.delete()
            return JsonResponse({'status':200, 'msg': '删除成功'})
        except Exception as e:
            return JsonResponse({'status':404, 'msg': str(e)})



