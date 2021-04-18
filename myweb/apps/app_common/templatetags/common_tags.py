from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter

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
