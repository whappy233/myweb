# Django项目设置全局的模版变量

# settings.py文件中，在 TEMPLATES 中添加刚才写的方法引用
# TEMPLATES = [
#     {
#         'BACKEND': 'django.template.backends.django.DjangoTemplates',
#         'DIRS': [],
#         'APP_DIRS': True,
#         'OPTIONS': {
#             'context_processors': [
#                 'django.template.context_processors.debug',
#                 'django.template.context_processors.request',
#                 'django.contrib.auth.context_processors.auth',
#                 'django.contrib.messages.context_processors.messages',

#                 # --------------------------------
#                 # 自定义模版全局变量(默认变量)
#                 'myweb.contexts.carlos',
#                 # --------------------------------
#             ],
#         },
#     },
# ]


from django.utils import timezone
def carlos(request):
    username = request.user.username
    html = f'''
    <i data-toggle="tooltip" title="这是一个全局context" data-placement="right">
    当前用户:({username}){timezone.now()}
    </i>'''
    return {'Carlos': html}
