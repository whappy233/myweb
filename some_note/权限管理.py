
# 自带的权限管理 Django Permission系统

# Django中每个model被创建后后，Django默认都会添加该model的add, change和delete三个permission
# 定义一个名为Document的模型后，Django会自动创建相应的三个permission：add_document, change_document和delete_document

# 使用Django自带Permission权限管理系统分2两步: 
#   第一步是给用户设置相应的权限
#   第二步是在模板和视图里判断用户是否有相应的权限


# 在模板中判断用户是否有权限
# 在模板中可以使用全局变量perms来判断当前用户的所有权限
'''
{% if request.user.is_authenticated %}    # 首先需要登录
    {% if perms.smartdoc.add_document %}  # perms.应用名.add_模型名小写  (是否有添加权限)
        do something
    {% endif %}
{% endif %}
'''


# 在视图中判断用户是否有权限
# 在视图中可以使用 user.has_perm() 方法来判断一个用户是不是有相应的权限, 
# 当然最快捷的方式是使用 @permission_required 这个装饰器，
# 这样能够分离权限验证和核心的业务逻辑，使代码更简洁，逻辑更清晰。
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView, UpdateView
from django.http import Http404

# 只有已登录且有添加产品权限的用户才能创建产品
@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('smartdoc.add_product', raise_exception=True), name='dispatch')
class ProductCreate(CreateView):
    ...
# 强行访问无权限的页面只会出现403错误

# Django自带的permission系统只对模型有用，而不是针对某个具体的object。一旦用户获得编辑文档的权限，那么该用户将获得编辑所有文档的权限
@method_decorator(permission_required('smartdoc.change_product', raise_exception=True), name='dispatch')
class ProductUpdate(UpdateView):
    ...

    def get_object(self, queryset=None):  # 通过get_object方法用户只能修改自己的的文档
        obj = super().get_object(queryset=queryset)
        if obj.author != self.request.user:
            raise Http404()
        return obj