from django.shortcuts import render
from django.http import HttpResponse, Http404, StreamingHttpResponse, FileResponse
from django.views.generic import ListView, DetailView
from .models import Gallery, Photo
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import os


# 相册列表
# 使用基于类的视图时，需要按如下方法使用method_decorator的这个装饰器。其作用是把类伪装成函数，然后再应用login_required这个装饰器
# 或者在url中使用 path('', login_required(views.GalleryListView.as_view()), name='gallery_list')
@method_decorator(login_required, name='dispatch')
class GalleryListView(ListView):
    queryset = Gallery.objects.filter(is_visible=True)
    paginate_by = 12
    template_name = 'app_gallery/gallery_list.html'  # 使用自定义模板渲染

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'gallery'
        return context


# 相册详细
# 使用基于类的视图时，需要按如下方法使用method_decorator的这个装饰器。其作用是把类伪装成函数，然后再应用login_required这个装饰器
# 或者在url中使用 re_path('xxx', login_required(views.GalleryDetail.as_view()), name='gallery_detail'),
@method_decorator(login_required, name='dispatch')
class GalleryDetail(DetailView):
    model = Gallery
    template_name = 'app_gallery/gallery_detail.html'  # 使用自定义模板渲染
    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['images'] = Photo.objects.filter(gallery=self.object.id) # 相册下的所有文件
        context['section'] = 'gallery'
        return context






# 该方法有个问题，如果文件是个二进制文件，HttpResponse输出的将会是乱码。
# 对于一些二进制文件(图片，pdf)，我们更希望其直接作为附件下载
def file_download(request, file_path):
    # do something...
    with open(file_path) as f:
        c = f.read()
    return HttpResponse(c)


def media_file_download(request, file_path):
    with open(file_path, 'rb') as f:
        try:
            response = HttpResponse(f)
            response['content_type'] = "application/octet-stream"
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
            return response
        except Exception:
            raise Http404


# HttpResponse 有个很大的弊端，其工作原理是先读取文件，载入内存，然后再输出。如果下载文件很大，该方法会占用很多内存。
# 对于下载大文件，Django 更推荐 StreamingHttpResponse 和 FileResponse 方法，这两个方法将下载文件分批 (Chunks) 写入用户本地磁盘，先不将它们载入服务器内存
def stream_http_download(request, file_path):
    try:
        response = StreamingHttpResponse(open(file_path, 'rb'))
        response['content_type'] = "application/octet-stream"
        response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
        return response
    except Exception:
        raise Http404


# FileResponse方法是SteamingHttpResponse的子类
# 加上 @login_required 装饰器，可以实现用户需要先登录才能下载某些文件的功能
def file_response_download1(request, file_path):
    try:
        response = FileResponse(open(file_path, 'rb'))
        response['content_type'] = "application/octet-stream"
        response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
        return response
    except Exception:
        raise Http404


# 上面定义的下载方法可以下载所有文件，不仅包括.py文件，还包括不在media文件夹里的文件(比如非用户上传的文件)。
# 比如当我们直接访问127.0.0.1:8000/file/download/file_project/settings.py/时，你会发现我们连file_project目录下的settings.py都下载了。
# 所以我们在编写下载方法时，我们一定要限定那些文件可以下，哪些不能下或者限定用户只能下载media文件夹里的东西
def file_response_download(request, file_path):
    ext = os.path.basename(file_path).split('.')[-1].lower()
    # cannot be used to download py, db and sqlite3 files.
    if ext not in ['py', 'db',  'sqlite3']:
        response = FileResponse(open(file_path, 'rb'))
        response['content_type'] = "application/octet-stream"
        response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
        return response
    else:
        raise Http404

# 然而即使加上了@login_required的装饰器，用户只要获取了文件的链接地址, 他们依然可以通过浏览器直接访问那些文件。
# 保护文件的链接地址和文件私有化
# 文件私有化的两种方法
# 如果你想实现只有登录过的用户才能查看和下载某些文件，大概有两种方法，这里仅提供思路。
# 上传文件放在media文件夹，文件名使用很长的随机字符串命名(uuid), 让用户无法根据文件名猜出这是什么文件。
# 视图和模板里验证用户是否已登录，登录或通过权限验证后才显示具体的url。- 简单易实现，安全性不高，但对于一般项目已足够。

# 上传文件放在非media文件夹，用户即使知道了具体文件地址也无法访问，因为Django只会给media文件夹里每个文件创建独立url资源。
# 视图和模板里验证用户是否已登录，登录或通过权限验证后通过自己编写的下载方法下载文件。- 安全性高，但实现相对复杂