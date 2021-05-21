

# 在文件上传过程中，实际的文件数据存储在 request.FILES 中。这个字典中的每一个条目都是一个 UploadedFile 对象.
f = request.FILES['form_file_name']
f.read()                # 请勿读取大文件(将文件全加载到内存!)
f.multiple_chunks()     # 如果上传的文件足够大，需要分块读取，返回 True。默认情况下是大于 2.5 兆字节的文件，但这是可以配置的
f.chucks()              # 一个生成器，返回文件的块。如果 multiple_chunks() 是 True, 应该使用 chucks(),在实践中，
# 通常最简单的做法是一直使用 chunks()。循环使用 chunks() 而不是使用 read() 可以确保大文件不会过度占用系统的内存
with open('some/file/name.txt', 'wb+') as destination:
    for chunk in f.chunks():
        destination.write(chunk)

# 像普通的 Python 文件一样，你可以通过迭代上传的文件来逐行读取文件：
for line in f:
    ... # do_something_with(line)

f.name  
# 上传的文件名称（如 my_file.txt）。

f.size  
# 上传文件的大小，以字节为单位。

f.content_type  
# 与文件一起上传的内容类型头（例如 text/plain 或 application/pdf）。
# 就像用户提供的任何数据一样，你不应该相信上传的文件实际上是这种类型。你仍然需要验证该文件是否包含内容类型头所声称的内容 —— '信任但验证'。

f.content_type_extra
# 包含传递给 content-type 头的额外参数的字典。
# 这通常是由服务提供的，比如 Google App Engine，它代表你拦截和处理文件上传。
# 因此，您的处理程序可能不会收到上传的文件内容，而是收到一个 URL 或其他指向文件的指针（参见 RFC 2388）。

f.charset
# 对于 text/* 内容类型，浏览器提供的字符集（即 utf8）。同样，'信任但验证' 是这里的最佳政策。


# ------------------------------------------------------------------------------------
'内置上传处理程序'
    # MemoryFileUploadHandler 和 TemporaryFileUploadHandler 共同提供了 Django 默认的文件上传行为，
    # 即向内存中读取小文件，向磁盘中读取大文件。它们位于 django.core.files.uploadhandler 中。

    # MemoryFileUploadHandler
    # 文件上传处理程序，将上传的文件以流式传输到内存中（用于小文件）。

    # TemporaryFileUploadHandler
    # 使用 TemporaryUploadedFile 将数据流式传输到临时文件的上传处理程序。

    # settings.py: 默认程序
    # 上传处理程序是按顺序处理的
    FILE_UPLOAD_HANDLERS =[
            'django.core.files.uploadhandler.MemoryFileUploadHandler',
            'django.core.files.uploadhandler.TemporaryFileUploadHandler',
        ]


'编写自定义上传处理程序'
    # 使用自定义的 handlers 来强制处理用户层面的配额，动态压缩数据，渲染进度条，甚至可以将数据发送到其他存储地址而不是本地
    # 所有的文件上传处理程序应该是 django.core.files.uploadhandler.FileUploadHandler 的子类
    # 你可以在任何地方定义上传处理程序

    '''必要方法'''
        'receive_data_chunk(raw_data, start)'  # 用于接收文件上传的 '块' 数据
            # raw_data 是一个包含上传数据的字节字符串。
            # start 是文件中 raw_data 块开始的位置。

            # 你返回的数据将被输入到后续的上传处理程序的 receive_data_chunk 方法中。通过这种方式，一个处理程序可以成为其他处理程序的 '过滤器'。
            # 从 receive_data_chunk 中返回 None，以短路剩余的上传处理程序。如果你自己存储上传的数据，并且不希望后续的处理程序存储数据的副本，这很有用。
            # 如果引发一个 StopUpload 或 SkipFile 异常，上传将被中止或文件将被完全跳过。

        'file_complete(file_size)'  # 当文件上传完毕时调用

            # 处理程序应返回一个 UploadedFile 对象，该对象将存储在 request.FILES 中。
            # 处理程序也可以返回 None 以表明 UploadedFile 对象应来自后续的上传处理程序。

    '''可选方法'''
        'chunk_size'
            # Django 应该存储到内存中并反馈给处理程序的 '块' 的大小，以字节为单位。
            # 也就是说，这个属性控制了输入到 receive_data_chunk 的数据块的大小。

            # 为了获得最大的性能，分块大小应该被 4 整除，并且大小不能超过 2GB（231 字节）。
            # 当有多个处理程序提供的多个分块大小时，Django 将使用所有处理程序中定义的最小分块大小。

            # 默认为 64*210 字节，即 64KB。

        'new_file(field_name, file_name, content_type, content_length, charset, content_type_extra)'
            # 回调信号，表示一个新的文件上传开始。在任何数据被送入任何上传处理程序之前，这个回调被调用。

            # field_name        是文件 <input> 字段的字符串名称。
            # file_name         是浏览器提供的文件名。
            # content_type      是浏览器提供的 MIME 类型 —— 例如 'image/jpeg'。
            # content_length    是浏览器给出的图像长度。有时不会提供，而是 None。
            # charset           是浏览器提供的字符集（即 utf8）。与 content_length 一样，有时不会提供。
            # content_type_extra 是关于文件的 content-type 头的额外信息。参见 UploadedFile.content_type_extra。

            # 这个方法可能会引发一个 StopFutureHandlers 异常，以防止后续处理程序处理这个文件。

        'upload_complete()'
            # 回调信号，表示整个上传（所有文件）已经完成。

        'handle_raw_input(input_data, META, content_length, boundary, encoding)'
            # 允许处理程序完全覆盖原始 HTTP 输入的解析。

            # input_data            是一个支持 read()-ing 的类文件对象。
            # META 与 request.META  是同一个对象。
            # content_length        是 input_data 中数据的长度。不要从 input_data 中读取超过 content_length 的字节。
            # boundary              是本次请求的 MIME 边界。
            # encoding              是请求的编码。

            # 如果想继续上传处理，则返回 None，如果想直接返回适合请求的新数据结构，则返回 (POST，FILES) 的元组。


'动态修改上传处理程序'
    # 有时候某些视图需要不同的上传行为。在这些例子里，你可以基于每个请求覆盖上传处理程序。
    # 默认情况下，这个列表将包含由 FILE_UPLOAD_HANDLERS 设置的上传处理程序，但你可以像修改其他列表一样修改这个列表。

    # 假设你正在编写 ProgressBarUploadHandler ，来提供在上传过程中的反馈给 Ajax widget。你需要添加这个处理程序到你的上传处理模块：
    'request.upload_handlers.insert(0, ProgressBarUploadHandler(request))'

    # 如果你想完全替换上传处理程序，你需要指定新列表：
    "request.upload_handlers = [ProgressBarUploadHandler(request)]"


    # 你只能在访问 request.POST 或 request.FILES 之前修改上传处理程序
    # 由于 request.POST 由 CsrfViewMiddleware 访问，默认情况下已开启。
    # 这意味着你需要在视图上使用 csrf_exempt() 来允许你改变上传处理程序。
    # 然后你需要在实际处理请求的函数上使用 csrf_protect() 。
    # 注意这可能会让处理程序在 CSRF 检测完成之前开始接受文件上传。示例：
    from django.views.decorators.csrf import csrf_exempt, csrf_protect
    @csrf_exempt
    def upload_file_view(request):
        request.upload_handlers.insert(0, ProgressBarUploadHandler(request))
        return _upload_file_view(request)

    @csrf_protect
    def _upload_file_view(request):
        ... # Process request



# ------------------------------------------------------------------------------------
'上传多个文件'
    # 如果你想使用一个表单字段上传多个文件，则需要设置字段的 widget 的 multiple HTML 属性。

    # 1. forms.py
    from django import forms
    class FileFieldForm(forms.Form):
        file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    # 2. 然后覆盖 FormView 子类的 post 方法来控制多个文件上传：
    # views.py
    from django.views.generic.edit import FormView
    from .forms import FileFieldForm
    class FileFieldView(FormView):
        form_class = FileFieldForm
        template_name = 'upload.html'  # 使用的模板.
        success_url = '...'  # 成功后的跳转地址.

        def post(self, request, *args, **kwargs):
            form_class = self.get_form_class()  # FileFieldForm
            form = self.get_form(form_class)    # Form 实例化
            files = request.FILES.getlist('file_field')
            if form.is_valid():
                for f in files:
                    ...  # 对每个文件执行操作
                return self.form_valid(form)
            else:
                return self.form_invalid(form)