

from rest_framework.views import APIView
from rest_framework.parsers import BaseParser, JSONParser, FormParser, MultiPartParser, FileUploadParser,
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.decorators import parser_classes


'''
解析器
    当访问request.data时，REST框架将检查传入请求中的Content-Type头，并确定用于解析请求内容的解析器


JSONParser:
    解析 JSON 请求内容。
    .media_type: application/json

FormParser:
    解析 HTML 表单内容。request.data将被填充一个QueryDict的数据。
    通常, 你需要使用FormParser和MultiPartParser两者, 以便完全支持HTML表单数据。
    .media_type: application/x-www-form-urlencoded

MultiPartParser:
    解析多部分HTML表单内容, 支持文件上传。request.data 都将被一个 QueryDict填充。
    你通常会同时使用FormParser和MultiPartParser两者, 以便完全支持HTML表单数据。
    .media_type: multipart/form-data

FileUploadParser:
    解析原始文件上传内容。 request.data 属性将是有单个key 'file'的包含上传文件的字典。
    如果与FileUploadParser一起使用的视图使用filename URL关键字参数调用, 则该参数将用作文件名。
    如果没有filename URL关键字参数调用, 那么客户端必须在Content-Disposition HTTP头中设置文件名。
    例如 Content-Disposition: attachment; filename=upload.jpg.
    .media_type: */*

    NOTE:
    FileUploadParser 用于与原始数据请求一起上传文件的本机客户端。
    对于基于Web的上传, 或者对于具有多部分上传支持的本机客户端, 您应该使用MultiPartParser解析器。
    由于该解析器的media_type与任何内容类型匹配, 所以FileUploadParser通常应该是API视图中唯一的解析器。
    FileUploadParser 遵循 Django 的标准 FILE_UPLOAD_HANDLERS 设置, 和 request.upload_handlers 属性。

    基本用法示例：
    `
    # views.py
    class FileUploadView(views.APIView):
        parser_classes = (FileUploadParser,)

        def put(self, request, filename, format=None):
            file_obj = request.data['file']
            # ...
            # do some stuff with uploaded file
            # ...
            return Response(status=204)

    # urls.py
    urlpatterns = [
        # ...
        url(r'^upload/(?P<filename>[^/]+)$', FileUploadView.as_view())
    ]
    `
'''

# 基本使用

# 全局设置:
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    )
}

# 在单个视图中设置
# 类视图
class ExampleView(APIView):
    """
    可以接收JSON内容POST请求的视图。
    """
    parser_classes = (JSONParser,)

    def post(self, request, format=None):
        return Response({'received data': request.data})

# 函数视图
@api_view(['POST'])
@parser_classes((JSONParser,))
def example_view(request, format=None):
    """
    可以接收JSON内容POST请求的视图
    """
    return Response({'received data': request.data})



'''
自定义解析器

要实现一个自定义解析器, 你应该重写 BaseParser, 设置 .media_type 属性, 并实现 .parse(self, stream, media_type, parser_context) 方法。
该方法应该返回用于填充request.data 属性的数据。
传递给 .parse() 的参数是:
    stream: 表示请求体的数据流

    media_type :可选的。如果提供, 这是传入请求内容的媒体类型。
                基于请求的Content-Type:头, 这可能比渲染器的media_type属性更具体, 可能包括媒体类型参数。
                例如 "text/plain; charset=utf-8"。

    parser_context: 可选的。如果提供, 该参数将是一个包含解析请求内容可能需要的任何附加上下文的字典。
                    默认情况下将包含以下keys: view, request, args, kwargs。
'''
# 以下是一个Plain text的示例, 它将使用表示请求正文的字符串填充request.data属性。

class PlainTextParser(BaseParser):
    """
    Plain text 解析器。
    """
    media_type = 'text/plain'

    def parse(self, stream, media_type=None, parser_context=None):
        """
        只需返回一个表示请求正文的字符串。
        """
        return stream.read()
