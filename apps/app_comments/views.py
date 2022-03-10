

import json

from app_blog.models import Article
from myweb.utils import JSONEncoder, validateEmail
from app_user.models import UserProfile

from django import forms
from django.apps import apps
from django.contrib.auth import get_user_model
from django.core import serializers
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.forms.models import modelform_factory
from django.forms.utils import ErrorDict
from django.http import QueryDict, request
from django.http.response import (Http404, HttpResponse, HttpResponseForbidden,
                                  JsonResponse)
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic.edit import FormView
from django.views.generic.list import BaseListView, View
from loguru import logger

from .forms import CommentForm
from .models import Comments, MpComments

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


class CommentsView(BaseListView):
    model = Comments
    paginate_by = 5

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()

        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if self.get_paginate_by(self.object_list) is not None and hasattr(self.object_list, 'exists'):
                is_empty = not self.object_list.exists()
            else:
                is_empty = not self.object_list
            if is_empty:
                raise Http404(_("Empty list and '%(class_name)s.allow_empty' is False.") % {
                    'class_name': self.__class__.__name__,
                })

        try:
            context = self.get_context_data()
        except Exception as e:
            print(e)
            if request.is_ajax():
                return HttpResponse({'status':404, 'data': None})
            else:
                raise e

        if request.is_ajax():
            paginator = context['paginator']
            page_obj = context['page_obj']
            is_paginated = context['is_paginated']
            object_list = context['object_list']

            serialize_items = serializers.serialize("json", object_list,
                                                    fields=('body', 'mood', 'img', 'created'),
                                                    ensure_ascii=False)

            data = {
                'status': 200,
                'current_page': page_obj.number,    # 当前页码
                'has_next': page_obj.has_next(),    # 是否有下页
                'page_total': paginator.num_pages,  # 总页数
                'items_count': paginator.count,     # 元素总数
                'data': serialize_items,
            }

            return JsonResponse(data, encoder=JSONEncoder)

        return self.render_to_response(context)



class CommentsView(View):
    paginate_by = 5

    # 查询评论
    def get(self, request, *args, **kwargs):
        '''
        /comment/?content_type=article&object_id=1
        content_type: 关联模型名称 Model name
        object_id: 关联模型实例 ID
        '''

        try:
            content_type_model = request.GET['content_type']
            object_id = int(request.GET['object_id'])
            page = int(request.GET.get('page', 0))

            if page:
                start = self.paginate_by * (page-1)
                end = self.paginate_by * page
            else:
                start = end = None
        except Exception as e:
            return HttpResponse(json.dumps({'status':403,'err_msg':'请求参数错误'}, ensure_ascii=False), content_type="application/json; charset=UTF-8")
        
        comments = self.get_comments(start, end, serialize=True, content_type_model=content_type_model, object_id=object_id)
        if len(comments) < 1:
            return HttpResponse(json.dumps({'status':404,'err_msg':'请求数据为空'}, ensure_ascii=False), content_type="application/json; charset=UTF-8")

        data = {'status': 200, 'current_page':page, 'comments': comments}
        json_data = json.dumps(data, cls=JSONEncoder, separators=(',',':'))
        return HttpResponse(json_data, content_type="application/json; charset=UTF-8")

    def get_comments(self, start, end, serialize, content_type_model, object_id):
        cache_key = f'comments_s_{start}_e_{end}_ser_{serialize}_ctm_{content_type_model}_oid_{object_id}'
        data = cache.get(cache_key)
        if data != None:
            logger.info(f'获取文章评论缓存:{cache_key}')
            return data
        else:
            data = Comments.objects.show(start, end, serialize=True, content_type__model=content_type_model, object_id=object_id)
            cache.set(cache_key, data, 60 * 100)
            logger.info(f'设置文章评论缓存:{cache_key}')
            return data

    # 增加评论
    def post(self, request, *args, **kwargs):
        if request.is_ajax():   

            article_slug = request.POST.get('object_slug', '')
            comment_body = request.POST.get('comment_body', '')

            replyto = request.POST.get('replyto', '')

            username = request.POST.get('username', '')
            nickname = request.POST.get('nickname', '')
            email = request.POST.get('email', '')

            if article_slug and comment_body:
                try:
                    article = Article.objects.get(slug=article_slug)
                except:
                    return JsonResponse({'status': 404, 'msg':'数据获取失败'})

                if request.user.is_authenticated and request.user.username==username:
                    wanderer = False
                    author = request.user.profile
                elif username and not (nickname and email):
                    return JsonResponse({'status': 402, 'msg':'页面过期请刷新页面'}) 
                else:
                    if not 0 < len(str(nickname)) < 20:
                        return JsonResponse({'status': 401, 'msg':'请求数据非法(nickname 控制在20字以内)'}) 
                    if not 0 < len(str(email)) < 50:
                        return JsonResponse({'status': 401, 'msg':'请求数据非法(email 控制在50字以内)'}) 
                    if not validateEmail(email):
                        return JsonResponse({'status': 401, 'msg':'请求数据非法(Email 格式错误)'}) 
                    if UserProfile.objects.filter(w_email=email).exists():
                        return JsonResponse({'status': 401, 'msg':f'{email} 已存在'})
                    try:
                        author = UserProfile.objects.create(w_name=nickname, w_email=email)
                        wanderer = True
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
                    ip = request.META.get('REMOTE_ADDR')  # 这里获得代理ip
                    comment = Comments.objects.create(
                        body=comment_body,
                        author=author,
                        parent_comment=parent_comment,
                        ip_address=ip,
                        content_object=article
                    )
                    # mpcomment = MpComments.objects.create(
                    #     body=comment_body,
                    #     author=author,
                    #     parent=parent_comment,
                    #     ip_address=ip,
                    #     content_object=article
                    # )

                    # print(20*'++++++++++++++')
                    # print(mpcomment)
                except Exception as e:
                    if wanderer:
                        author.delete()
                    return JsonResponse({'status': 401, 'msg':e})
                return JsonResponse({'status': 200, 'msg':'评论成功'})
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
        except (ObjectDoesNotExist, ValidationError):
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
                form.save(commit=True)
                result['msg'] = 'success'
                result['status'] = 200

            except Exception as e:
                result['msg'] = str(e)
                result['status'] = 403
        else:
            result['msg'] = ErrorDict(form.errors).as_json()
            result['status'] = 403

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



