from django.contrib.auth.models import User
from rest_framework.renderers import (BaseRenderer, 
                                      JSONRenderer,
                                      TemplateHTMLRenderer,
                                      StaticHTMLRenderer,
                                      BrowsableAPIRenderer,
                                      HTMLFormRenderer,
                                      MultiPartRenderer,)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, renderer_classes

from .serializers import UserSerializer


'''渲染器

    渲染器类的排序:
        指定你的API的渲染器类时要考虑到每个媒体类型要分配哪些优先级，这一点非常重要。
        如果一个客户端不能指定它可以接受的表示形式，例如发送一个Accept: */*头，或者不包含一个Accept头，
        那么REST框架将选择列表中用于响应的第一个渲染器。

        例如，如果你的API提供JSON响应和HTML可浏览的API，
        则可能需要将JSONRenderer设置为你的默认渲染器，
        以便向不指定Accept标头的客户端发送JSON响应。

        如果你的API包含可以根据请求提供常规网页和API响应的视图，
        那么你就可以考虑使用TemplateHTMLRenderer作为你的默认渲染器，
        以便能在那些发送破坏的接收头的旧版本的浏览器上能很好的展示。

JSONRenderer:

    使用utf-8编码将请求的数据渲染成JSON。
    请注意，默认样式是包括unicode字符，并使用没有不必要空格的紧凑样式渲染响应:

    {"unicode black star":"★","value":999}
    客户端还可以包含'indent'媒体类型参数，在这种情况下，返回的JSON将被缩进。例如Accept: application/json; indent=4。

    可以使用UNICODE_JSON和COMPACT_JSON更改默认JSON编码样式。

    .media_type: application/json
    .format: '.json'
    .charset: None

TemplateHTMLRenderer

    使用Django的标准模板将数据渲染成HTML。
    与其他渲染器不同，传递给Response的数据不需要序列化。此外，与其他渲染器不同，你可能希望在创建Response时包含一个template_name参数。
    TemplateHTMLRenderer将创建一个RequestContext，使用response.data作为上下文字典，并确定用于渲染上下文的模板名称。
    模板名称由（按优先顺序）确定：
        一个显式的template_name参数传递给响应。
        在类中显式定义.template_name属性。
        调用view.get_template_names（）的返回结果。

    示例:
        class UserDetail(generics.RetrieveAPIView):
            """
            返回给定用户的模板HTML表示的视图。
            """
            queryset = User.objects.all()
            renderer_classes = (TemplateHTMLRenderer,)

            def get(self, request, *args, **kwargs):
                self.object = self.get_object()
                return Response({'user': self.object}, template_name='user_detail.html')

    如果你正在构建使用 TemplateHTMLRenderer 和其他渲染类的网站，
    你应该考虑将TemplateHTMLRenderer列为renderer_classes列表中的第一个类，
    这样即使对于发送格式不正确的ACCEPT:头文件的浏览器它也将被优先排序.

    media_type: text/html
    .format: '.html'
    .charset: utf-8

StaticHTMLRenderer
    一个简单的渲染器，只需返回预渲染的HTML。
    与其他渲染器不同，传递给响应对象的数据应该是表示要返回的内容的字符串。

    例子:
        @api_view(('GET',))
        @renderer_classes((StaticHTMLRenderer,))
        def simple_html_view(request):
            data = '<html><body><h1>Hello, world</h1></body></html>'
            return Response(data)

    你可以使用StaticHTMLRenderer使用REST框架返回常规HTML页面，也可以从单个路径返回HTML和API响应。

    .media_type: text/html
    .format: '.html'
    .charset: utf-8

BrowsableAPIRenderer

HTMLFormRenderer

MultiPartRenderer

'''

# ----------------------------------------------------------------------------------------------------------------------------------------
# 设置渲染器
# 可以使用DEFAULT_RENDERER_CLASSES设置全局默认的渲染器集。例如，以下设置将使用JSON作为主要媒体类型，并且还包括自描述API。
# 全局设置
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    )
}

# 你还可以设置用于单个视图或视图集的渲染器，使用APIView类视图。

# 类视图
class UserCountView(APIView):
    """
    返回JSON格式活动用户数的视图。
    """
    renderer_classes = (JSONRenderer, )

    def get(self, request, format=None):
        user_count = User.objects.filter(active=True).count()
        content = {'user_count': user_count}
        return Response(content)

# 函数视图
@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def user_count_view(request, format=None):
    """
    返回JSON格式活动用户数的视图。
    """
    user_count = User.objects.filter(active=True).count()
    content = {'user_count': user_count}
    return Response(content)




'''
----------------------------------------------------------------------------------------------------------------------------------------
自定义渲染器:
    要实现自定义渲染器，你应该重写 BaseRenderer，设置 .media_type和.format属性，并且实现 .render(self, data, media_type=None, renderer_context=None) 方法。
    这个方法应当返回一个字节bytestring，它将被用于HTTP响应的主体。
    传递给 .render() 方法的参数是：
        data :                  请求数据，由 Response() 实例化设置。

        media_type=None:        可选的。如果提供，这是由内容协商阶段确定的所接受的媒体类型。
                                根据客户端的 Accept: 头，这可能比渲染器的 media_type 属性更具体，可能包括媒体类型参数。
                                例如 "application/json; nested=true"。

        renderer_context=None:  可选的。如果提供，这是一个由view提供的上下文信息的字典。
                                默认情况下这个字典会包括以下键： view, request, response, args, kwargs。
'''

# 例子
# 下面是一个示例明文渲染器，它将使用参数作为响应 data 的内容返回响应。
class PlainTextRenderer(BaseRenderer):
    media_type = 'text/plain'
    format = 'txt'

    def render(self, data, media_type=None, renderer_context=None):
        return data.encode(self.charset)

# 设置字符集
# 假设默认的渲染器类正在使用 UTF-8 编码。要使用其他编码，请在渲染器设置 charset 属性。
class PlainTextRenderer(BaseRenderer):
    media_type = 'text/plain'
    format = 'txt'
    charset = 'iso-8859-1'

    def render(self, data, media_type=None, renderer_context=None):
        return data.encode(self.charset)

# 注意，如果一个渲染类返回了一个unicode字符串，则响应内容将被Response类强制转换成bytestring，渲染器上的设置的 charset 属性将用于确定编码。
# 如果渲染器返回一个bytestring表示原始的二进制内容，则应该设置字符集的值为 None，确保响应请求头的 Content-Type 中不会设置 charset 值。
# 在某些情况下你可能还需要将 render_style 属性设置成 'binary'。这么做也将确保可浏览的API不会尝试将二进制内容显示为字符串。
class JPEGRenderer(BaseRenderer):
    media_type = 'image/jpeg'
    format = 'jpg'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        return data


'''
----------------------------------------------------------------------------------------------------------------------------------------
高级渲染器使用
    你可以使用REST framework的渲染器做一些非常灵活的事情。一些例子...

    1.根据请求的媒体类型，从同一个路径既能提供单独的或者嵌套的表示。
    2.提供常规HTML网页和来自同一路径的基于JSON的API响应。
    3.为API客户端指定要使用的多种类型的HTML表示形式。
    5.未指定渲染器的媒体类型，例如使用 media_type = 'image/*'，并使用 Accept 标头来更改响应的编码。

'''    
# 媒体类型的不同行为
#   在某些情况下，你可能希望视图根据所接受的媒体类型使用不同的序列化样式。
#   如果你需要实现这个功能，你可以根据 request.accepted_renderer 来确定将用于响应的协商渲染器。
# 例如:
@api_view(('GET',))
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def list_users(request):
    """
    一个可以返回系统中用户的JSON或HTML表示的视图。
    """
    queryset = User.objects.filter(active=True)

    if request.accepted_renderer.format == 'html':
        # TemplateHTMLRenderer 采用一个上下文的字典，
        # 并且额外需要一个 'template_name'。
        # 它不需要序列化。
        data = {'users': queryset}
        return Response(data, template_name='list_users.html')

    # JSONRenderer 需要正常的序列化数据。
    serializer = UserSerializer(instance=queryset)
    data = serializer.data
    return Response(data)


# 不明确的媒体类型
#   在某些情况下你可能希望渲染器提供一些列媒体类型。 在这种情况下，你可以通过为 media_type 设置诸如 image/* 或 */*这样的值来指定应该响应的媒体类型。
#   如果你指定了渲染器的媒体类型，你应该确保在返回响应时使用 content_type 属性明确指定媒体类型。 
# 例如:
# return Response(data, content_type='image/png')
