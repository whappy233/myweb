from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter
from ..models import Carousel


register = template.Library()

# 渲染蜜罐
@register.inclusion_tag('app_common/snippets/honeypot_field.html', takes_context=True)
def render_honeypot_field(context, field_name=None):
    """
    呈现名为 field_name 的蜜罐字段（默认为 HONEYPOT_FIELD_NAME )
    """
    if not field_name:
        field_name = getattr(settings, 'HONEYPOT_FIELD_NAME', 'name1')
    value = getattr(settings, 'HONEYPOT_VALUE', '')
    if callable(value):
        value = value()
    return {'fieldname': field_name, 'value': value}



# 获取轮播图片列表
@register.simple_tag
def get_carousel_list():
    '''获取轮播图片列表'''
    return Carousel.objects.all()


class SetVarNode(template.Node):

    def __init__(self, var_name, var_value):
        self.var_name = var_name
        self.var_value = var_value

    def render(self, context):
        try:
            value = template.Variable(self.var_value).resolve(context)
        except template.VariableDoesNotExist:
            value = ""
        context[self.var_name] = value
        return ""


class VarAddOneNode(template.Node):

    def __init__(self, var_name):
        self.var_name = var_name

    def render(self, context):
        try:
            value = template.Variable(self.var_name).resolve(context)
            context[self.var_name] = str(int(value) + 1)
        except template.VariableDoesNotExist:
            value = ""
        return ""



@register.tag(name='set')
def set_var(parser, token):
    """
      在django模板中定义变量 
      {% set a = 123 %}
      {% set a++ %}
    """
    parts = token.split_contents()
    print('len(parts)=' + str(len(parts)))
    if len(parts) == 2:
        content = parts[1]
        if content[len(content)-2:len(content)] == '++':
            var_name = content[:len(content) - 2]
            return VarAddOneNode(var_name)
        else:
            return ""
    elif len(parts) == 4:
        return SetVarNode(parts[1], parts[3])
        # raise template.TemplateSyntaxError("'set'标签的格式必须为: {％set <var_name> = <var_value>％}")



