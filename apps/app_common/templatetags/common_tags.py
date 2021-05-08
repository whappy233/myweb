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



# django/template/context.py

# 在模板定义变量
@register.tag(name='set')
def set_var(parser, token):
    """
      在django模板中定义变量 
      {% set a = 123 %}
      {% set a++ %}
    """
    parts = token.split_contents()

    if len(parts) == 2:  # ['set', 'left++']
        content = parts[1]
        if content[len(content)-2:len(content)] == '++':
            var_name = content[:len(content) - 2]
            return VarAddOneNode(var_name)
        else:
            return ""
    elif len(parts) == 4:  # ['set', 'left', '=', '0']
        return SetVarNode(parts[1], parts[3])
    else:
        raise template.TemplateSyntaxError("'set'标签的格式必须为: {％set <var_name> = <var_value>％}")


class SetVarNode(template.Node):
    def __init__(self, var_name, var_value):
        self.var_name = var_name
        self.var_value = var_value

    def render(self, context):
        try:
            template.Variable(self.var_name).resolve(context)
            # 如果存在于当前上下文中，则在其中一个上下文中设置一个变量(找到的第一个)
            context.set_upward(self.var_name, self.var_value)
        except template.VariableDoesNotExist:
            context[self.var_name] = self.var_value
        return ""


class VarAddOneNode(template.Node):
    ''' ++ '''

    def __init__(self, var_name):
        self.var_name = var_name

    def render(self, context):
        try:
            value = template.Variable(self.var_name).resolve(context)
            # 如果存在于当前上下文中，则在其中一个上下文中设置一个变量(找到的第一个)
            context.set_upward(self.var_name, int(value)+1)
            # context[self.var_name] = str(int(value) + 1)
        except template.VariableDoesNotExist:
            ...
        return ""


# 在模板定义 list
@register.tag(name='setList')
def set_list(parser, token):
    """
    在模板定义临时列表
    用法 : {% setList par1 par2 ... parN as listName %}
    `par` 可以为一个简单变量或者列表.
    设置空列表: {% setList '' as listName %}
    """
    data = token.split_contents()
    if len(data) >= 4 and data[-2] == "as":
        listName = data[-1]
        items = data[1:-2]
        return SetListNode(items, listName)
    else:
        raise template.TemplateSyntaxError("'setList'标签的格式必须为 : {% setList par1 par2 ... parN as listName %}")


class SetListNode(template.Node):
    def __init__(self, items, listName):
        self.items = []
        for item in items:
            self.items.append(template.Variable(item))
        self.listName = listName

    def render(self, context):
        finalList = []
        for item in self.items:
            itemR = item.resolve(context)
            if isinstance(itemR, list):
                finalList.extend(itemR)
            elif itemR == '':
                pass
            else:
                finalList.append(itemR)
        context.set_upward(self.listName, list(finalList))
        return ""