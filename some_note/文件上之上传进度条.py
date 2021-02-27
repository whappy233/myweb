
# https://blog.csdn.net/jinhao7773/article/details/83356254


# 因为显示给每个用户每次浏览页面的时候，表单域的name都是相同的，为了区分每个页面，在表单提交的时候需要加上一个
# formhash 的 GET 参数，以此来区分文件上传来源
from django.core.files.uploadhandler import FileUploadHandler, MemoryFileUploadHandler
from django.core.cache import cache
from django.http.response import JsonResponse
class LogFileUploadHandler(FileUploadHandler):
    def __init__(self, request=None):
        super(LogFileUploadHandler, self).__init__(request)
        if 'formhash' in self.request.GET:
            self.formhash = self.request.GET['formhash']
            cache.add(self.formhash, {})
            self.activated = True
        else:
            self.activated = False

        # caches -> formhash: {field_name: '已上传大小'}
        # 当文件上传完成时, {field_name: -1}

    def new_file(self, *args, **kwargs):
        '''回调信号, 表示一个新的文件上传开始. 在任何数据被送入任何上传处理程序之前, 这个回调被调用'''
        super(LogFileUploadHandler, self).new_file(*args, **kwargs)
        if self.activated:
            fields = cache.get(self.formhash)
            fields[self.field_name] = 0
            cache.set(self.formhash, fields)

    def receive_data_chunk(self, raw_data, start):
        '''用于接收文件上传的 "块" 数据'''
        # time.sleep(5) for local test, it slow down the upload speed
        if self.activated:
            fields = cache.get(self.formhash)
            fields[self.field_name] = start
            cache.set(self.formhash, fields)
        return raw_data

    def file_complete(self, file_size):
        '''回调信号, 当文件上传完毕时调用'''
        if self.activated:
            fields = cache.get(self.formhash)
            fields[self.field_name] = -1
            cache.set(self.formhash, fields)

    def upload_complete(self):
        '''回调信号, 表示整个上传（所有文件）已完成'''
        if self.activated:
            fields = cache.get(self.formhash)
            fields[self.formhash] = -1
            cache.set(self.formhash, fields)


# 第一个问题,为什么formhash是一个GET参数，而不是POST参数，如果是POST的话不是更方便？因为只要在表单中加入一个hidden域即可。
    # 因为如果在 Handler 尝试存取 request.POST 中的值，会导致又一次调用 Upload Handler, 从而形成无限递归，所以只能存取request.GET中的值。
    # 当然这并不是什么大问题，后面我会讲到用 js 将 hidden 域中的 formhash 提取出来作为 GET 参数。

# 第二个问题是如何保存文件上传进度的数据?
    # 用数据库来保存显然是开销太大了，因为一次文件上传的过程中需要反复读写记录的数据。
    # 最终选择使用了 django 的 cache 组件来进行保存，因为保存的数据格式相对比较简单，并且对速度的要求比较高

# 第三个问题,经实践测试，upload handler 中的 self.content_length 似乎一直都为 None 所以在文件没有完整上传之前是没法获得总的数据长度的。
    # 因此此 handler 只记录了已上传的字节数，并且以 -1 表示上传结束。
    # 同样，为了表示一个表单中的所有文件上传域的文件上传完毕，通过将 formhash 作为 key，值为 -1 来表示



'''如何提交表单'''

# 在记录了文件上传进度数据后，接着的问题就是如何在文件边上传的过程中边间隔一定时间对进度进行刷新，
# 通常的做法是将表单提交到一个隐藏的iframe中，这里也不例外。

# 为了将原本不具有Ajax功能的表单变成异步的，并且需要在表单提交后不断查询处理进度，具体的过程是大致这样的：
# 1、在表单中添加一个hidden 域 formhash, 要求尽可能唯一，用来验证表单提交的来源。
# 2、通过js在表单的action地址末尾加上 "?formhash=hashstr" 形式的查询字符串, hashstr 通过 hidden 域的 formhash 提取而来
# 3、创建一个隐藏的 iframe, 并且将表单的 target 设置为该 iframe 的 name
# 4、写一个专门用来刷新表单文件上传进度的js函数, 通过 setTimeout 将该函数在过一定时间后执行,
#   同时在该函数内部根据服务器返回的进度数据决定是否需要递归调用setTimeout, 以便再次刷新.


# views.py
from functools import wraps
from django.urls import reverse
from django.shortcuts import render, redirect
from django.utils import simplejson
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.core.cache import cache
from hashlib import md5
import datetime
from django import forms
# from uploadhandler import LogFileUploadHandler
class AjaxHiddenWidget(forms.HiddenInput):
    def __init__(self, attrs=None):
        super(AjaxHiddenWidget, self).__init__(attrs)
        if 'interval' not in self.attrs:
            self.attrs['interval'] = 4000
        if 'hidden_iframe_name' not in self.attrs:
            self.attrs['hidden_iframe_name'] = 'hidden_iframe'

    def render(self, name, value, attrs=None):
        md5_ = md5()
        md5_.update(str(datetime.datetime.now()).encode('utf8'))
        formhash = value = md5_.hexdigest()
        process = reverse('uploads-process')
        final_attrs = self.build_attrs(
            attrs, name=name, formhash=formhash, process=process)
        result = super(AjaxHiddenWidget, self).render(name, value, attrs)
        # 加载js
        js = """
            <script src="/media/jquery-1.3.1.min.js"></script>
            <script>
                var default_interval = %(interval)s;
                function refresh(){
                    var formhash = "%(formhash)s";
                    var rnd = Math.random();
                    $.getJSON('%(process)s', {
                        'formhash': formhash,
                        'rnd': rnd,
                    }, function(data, textStatus){
                        var continue_refresh = true;
                        for (field_name in data) {
                            continue_refresh = continue_refresh && field_name != formhash;
                            if (data[field_name] == -1) {
                                var msg = "upload done";
                            }
                            else {
                                num = parseInt(data[field_name] / 1024);
                                var msg = "uploaded " + num + " KB";
                            }
                            $("input[name='" + field_name + "']").next().text(msg);
                        }
                        
                        if (continue_refresh) {
                            setTimeout(refresh, default_interval);
                        }
                    })
                };
                
                function bind_submit(){
                    $("form").submit(function(eventObject){
                        this['action'] = this['action'] + '?formhash=%(formhash)s' ;
                        $('<iframe name="%(hidden_iframe_name)s" id="id_%(hidden_iframe_name)s" style="display:none"></iframe>').appendTo("body");
                        this['target'] = '%(hidden_iframe_name)s';
                        $("input[type='file']").after("<span></span>");
                        setTimeout(refresh, default_interval);
                    });
                }
                $(document).ready(function(){
                    bind_submit();
                });
                
                function replace_iframe(){
                    $('body').html($('#id_%(hidden_iframe_name)s').contents().find('body').html());
                    bind_submit();
                }
            </script>
        """ % final_attrs

        return mark_safe(result+js)

    class Media:
        # 表示静态文件路径
        # 在模板中以 {{ forms.media }} 引入
        # 可以根据需要自己选择是使用 {{ form.media }} 还是直接将 j s文件的导入直接写在 render 方法中.
        js = ('/media/jquery-1.3.1.min.js', )


# 自定义 formField
class AjaxHiddenField(forms.CharField):
    widget = AjaxHiddenWidget()

    def __init__(self, *args, **kwargs):
        super(AjaxHiddenField, self).__init__(*args, **kwargs)


# 文件上传表单
class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()
    file2 = forms.FileField()
    formhash = AjaxHiddenField()



# django 处理表单提交的一般模式基本上所有处理都在一个view里，该view的内部逻辑可以分类3种情况：
# situation 1、直接的GET访问，这时只需要显示表单即可。
# situation 2、POST提交过来的，但是表单中包含错误数据，这时显示的页面需要同时包含这些错误提示。
# situation 3、POST提交过来的，并且表单成功处理，返回HttpResponseRedirect对象。

def make_ajax(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        # 在这里将自定义的 FileUploadHandler 插入到所有 FileUploadHandler 之前
        request.upload_handlers.insert(0, LogFileUploadHandler(request))
        response = view_func(request, *args, **kwargs)
        if 'formhash' in request.GET and isinstance(response, redirect):
            #situation 3
            location = response['Location']
            return HttpResponse('<script type="text/javascript">window.parent.location.href="%s"</script>' % location)
        elif 'formhash' in request.GET and isinstance(response, HttpResponse) and request.method == 'POST':
            #situation 2
            js = """
            <script type="text/javascript">
            $(document).ready(function(){ window.parent.replace_iframe(); })
            </script>
            """
            return HttpResponse(response.content + js)
        else:
            return response
    return wraps(view_func)(_wrapped_view_func)


@make_ajax
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # code handle form and file data
            return redirect('/uploads/succ/')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})


# 获取进度
def process(request):
    formhash = request.GET['formhash']
    status = cache.get(formhash)
    print(status)
    return JsonResponse(status)
