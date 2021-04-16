

from django import template
from django.contrib.auth import get_user_model



register = template.Library()


@register.simple_tag
def get_user(**kwargs):
    try:
        return get_user_model().objects.get(**kwargs)
    except Exception as e:
        return None
