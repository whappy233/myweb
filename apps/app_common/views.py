import os
import json

from django.conf import settings
from django.core.cache import cache
from django.shortcuts import render
from django.utils.timezone import now
from django.http import FileResponse, HttpResponse
from django.template.defaultfilters import filesizeformat
from django.views.decorators.csrf import csrf_exempt

from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

from .models import AboutBlog, FileSerializers, FileStorage




# rest_framework
class FileView(ModelViewSet):

    queryset = FileStorage.objects.filter()
    serializer_class = FileSerializers
    permission_classes = (permissions.IsAdminUser,)

    # 将request.user与author绑定
    def perform_create(self, serializer):
        file = self.request.data['file']
        serializer.save(name=file.name, size=filesizeformat(file.size))

    def perform_destroy(self, instance):
        instance.is_delete = True
        # 只需要更新 is_delete 的字段，而不是更新全表，减轻数据库写入的工作量
        instance.save(update_fields=['is_delete'])

    # /storage/files/3/download/
    @action(methods=['get', 'post'], detail=True)
    def download(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        response = FileResponse(open(instance.file.path, 'rb'))
        response['Content-Disposition'] = f'attachment;filename="{instance.name}"'
        return response


# 关于
def AboutView(request):
    obj = AboutBlog.objects.first()
    if obj:
        ud = obj.update_date.strftime("%Y%m%d%H%M%S")
        md_key = '{}_md_{}'.format(obj.id, ud)
        cache_md = cache.get(md_key)
        if cache_md:
            body = cache_md
        else:
            body = obj.body_to_markdown()
            cache.set(md_key, body, 3600 * 24 * 15)
    else:
        repo_url = 'https://github.com/Hopetree'
        body = '<li>作者 Github 地址：<a href="{}">{}</a></li>'.format(
            repo_url, repo_url)
    return render(request, 'blog/about.html', context={'body': body})



def xxxs(request):
    return render(request, 'tp/upload_process.html')



@csrf_exempt
def FileUploads(request):
    file = request.FILES.get('file')  # 获取文件对象，包括文件名文件大小和文件内容
    curttime = now().strftime("%Y%m%d")
    #规定上传目录
    upload_url = os.path.join(settings.MEDIA_ROOT,'attachment',curttime)
    #判断文件夹是否存在
    folder = os.path.exists(upload_url)
    if not folder:
        os.makedirs(upload_url)
        print("创建文件夹")
    if file:
        file_name = file.name
        #判断文件是是否重名，懒得写随机函数，重名了，文件名加时间
        if os.path.exists(os.path.join(upload_url,file_name)):
            name, etx = os.path.splitext(file_name)
            addtime = now().strftime("%Y%m%d%H%M%S")
            finally_name = name + "_" + addtime + etx
            #print(name, etx, finally_name)
        else:
            finally_name = file.name
 		#文件分块上传
        upload_file_to = open(os.path.join(upload_url, finally_name), 'wb+')
        for chunk in file.chunks():
            upload_file_to.write(chunk)
        upload_file_to.close()
		#返回文件的URl
        file_upload_url = settings.MEDIA_URL + 'attachment/' + curttime + '/' +finally_name
        #构建返回值
        response_data = {}
        response_data['FileName'] = file_name
        response_data['FileUrl'] = file_upload_url
        response_json_data = json.dumps(response_data)#转化为Json格式
        return HttpResponse(response_json_data)
