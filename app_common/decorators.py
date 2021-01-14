'''蜜罐验证装饰器'''


from functools import wraps
from django.conf import settings
from django.http import HttpResponseBadRequest
from django.template.loader import render_to_string


def honeypot_equals(val)->bool:
    """
        如果未指定 HONEYPOT_VERIFIER, 则使用默认验证程序。
        确保 val == HONEYPOT_VALUE 或 HONEYPOT_VALUE() (如果可调用)
    """
    expected = getattr(settings, 'HONEYPOT_VALUE', '')
    if callable(expected):
        expected = expected()
    return val == expected


def verify_honeypot_value(request, field_name):
    """
        Verify that request.POST[field_name] is a valid honeypot.
        Ensures that the field exists and passes verification according to
        HONEYPOT_VERIFIER.

        如果用户通过 POST 方式提交的表单里没有 honeypot 字段或该字段的值不等于settings.py中的默认值，则验证失败并返回如下错误
    """
    verifier = getattr(settings, 'HONEYPOT_VERIFIER', honeypot_equals)
    if request.method == 'POST':
        field = field_name or settings.HONEYPOT_FIELD_NAME
        if field not in request.POST or not verifier(request.POST[field]):
            response = render_to_string('app_common/snippets/honeypot_error.html', {'fieldname': field})
            return HttpResponseBadRequest(response)


def check_honeypot(func=None, field_name=None):
    """
        检查request.POST以获取有效的蜜罐字段
        如果未指定，则采用默认值为 HONEYPOT_FIELD_NAME 的可选 field_name
    """
    # hack to reverse arguments if called with str param
    # 如果使用 str param 进行调用，则会破解反向参数
    if isinstance(func, str):
        func, field_name = field_name, func

    def wrapper(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            response = verify_honeypot_value(request, field_name)
            if response:
                return response
            else:
                return func(request, *args, **kwargs)
        return inner

    if func is None:
        def decorator(func):
            return wrapper(func)
        return decorator

    return wrapper(func)


def honeypot_exempt(func):
    """
        豁免蜜罐验证
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    wrapper.honeypot_exempt = True
    return wrapper
