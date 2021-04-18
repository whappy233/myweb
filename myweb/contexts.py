'''Django项目设置全局的模版变量'''

# settings.py文件中，在 TEMPLATES 中添加刚才写的方法引用
# TEMPLATES = [
#     {
#         'BACKEND': 'django.template.backends.django.DjangoTemplates',
#         'DIRS': [],
#         'APP_DIRS': True,
#         'OPTIONS': {
#             'context_processors': [
#                 'django.template.context_processors.debug',
#                 'django.template.context_processors.request',   # 在模板中可以直接使用request对象
#                 'django.contrib.auth.context_processors.auth',  # 在模板里面可以直接使用user，perms对象
#                 'django.contrib.messages.context_processors.messages',  # 在模板里面可以直接使用message对象

#                  # 其他
#                 'django.template.context_processors.i18n'   # 在模板里面可以直接使用s ettings 的 LANGUAGES 和 LANGUAGE_CODE
#                 'django.template.context_processors.media'  # 可以在模板里面使用 settings 的 MEDIA_URL 参数
#                 'django.template.context_processors.csrf'   # 给模板标签 {% csrf_token %} 提供 token 值，默认总是开启。
#                 'django.template.context_processors.tz'     # 可以在模板里面使用 TIME_ZONE 参数

#                 # --------------------------------
#                 # 自定义模版全局变量(默认变量)
#                 'myweb.contexts.carlos',
#                 # --------------------------------
#             ],
#         },
#     },
# ]


# 自定义的全局上下文处理器本质上是个函数，使用它必须满足3个条件:
# 1. 传入参数必须有request对象  
# 2. 返回值必须是个字典 
# 3, 使用前需要在 settings 的 context_processors 里申明

# 内容处理器在所有使用 RequestContext 的请求中执行。
# 如果需要访问数据库，最好创建自定义模板标签，而不是使用内容处理器

# 全局上下文处理器提供的变量优先级高于单个视图函数给单个模板传递的变量。
# 这意味着全局上下文处理器提供的变量可能会覆盖你视图函数中自定义的本地变量，
# 因此请注意避免本地变量名与全局上下文处理器提供的变量名称重复

# 如果你希望单个视图函数定义的变量名覆盖全局变量，请使用以下强制模式:
# from django.template import RequestContext
# high_priority_context = RequestContext(request)
# high_priority_context.push({"my_name": "Adrian"})



from django.utils.safestring import mark_safe
from django.utils import timezone
def carlos(request):
    username = request.user.username
    html = f'''
    <i data-toggle="tooltip" title="这是一个全局context" data-placement="right">
    当前用户:({username}){timezone.now()}
    </i>'''
    return {'Carlos': mark_safe(html)}


# usage:
'''
{{ Carlos }}
'''