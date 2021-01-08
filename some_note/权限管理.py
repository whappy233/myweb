
'自带的权限管理 Django Permission系统'

# Django中每个model被创建后后，Django默认都会添加该model的add, change和delete三个permission
# 定义一个名为Document的模型后，Django会自动创建相应的三个permission：add_document, change_document和delete_document

# 使用Django自带Permission权限管理系统分2两步: 
#   第一步是给用户设置相应的权限
#   第二步是在模板和视图里判断用户是否有相应的权限


# 权限名一般由app名(app_label)，权限动作和模型名组成。以 app_blog 应用为例，Django为 Post 模型自动创建的4个可选权限名分别为:
# 查看文章(view): app_blog.view_post
# 创建文章(add): app_blog.add_post
# 更改文章(change): app_blog.change_post
# 删除文章(delete): app_blog.delete_post


'''
========================================================================
在模板中验证用户是否有权限
'''
# 在模板中可以使用全局变量 perms 来判断当前用户的所有权限
'''
{{ perms.app_blog }} 判断当前用户是否拥有 app_blog 应用下的所有权限

{% if request.user.is_authenticated %}    # 首先需要登录
    {% if perms.app_blog.add_post %}  # perms.应用名.add_模型名小写  (是否有添加权限)
        do something
    {% endif %}
{% endif %}
'''


'''
========================================================================
在视图中验证用户是否有权限
'''
# 在视图中可以使用 user.has_perm() 方法来判断一个用户是不是有相应的权限, 
# user_A.has_perm('app_blog.add_post')
# user_A.has_perm('app_blog.change_post)

# 如果我们要查看某个用户所在用户组的权限或某个用户的所有权限(包括从用户组获得的权限)，
# 我们可以使用 get_group_permissions() 和 get_all_permissions() 方法。
# user_A.get_group_permissions()  # 用户所在组的权限
# user_A.get_all_permissions()  # 用户所有权限

# 最快捷的方式是使用 @permission_required 这个装饰器
# 这样能够分离权限验证和核心的业务逻辑，使代码更简洁，逻辑更清晰。
# permission_required(perm, login_url=None, raise_exception=False)
# raise_exception=True, 会直接返回403无权限的错误
# 没有权限将会跳转到 login_url 指向的地址

# 如果你使用基于类的视图(Class Based View), 可以继承PermissionRequiredMixin这个类
# from django.contrib.auth.mixins import PermissionRequiredMixin
# class MyView(PermissionRequiredMixin, View):
    # permission_required = 'polls.can_vote'
    # Or multiple of permissions:
    # permission_required = ('polls.can_open', 'polls.can_edit')

from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView, UpdateView
from django.http import Http404

# 只有已登录且有添加产品权限的用户才能创建产品
# permission_required(perm, login_url=None, raise_exception=False)
@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('app_blog.add_post', raise_exception=True), name='dispatch')
class ProductCreate(CreateView):
    ...
# 强行访问无权限的页面只会出现403错误

# Django自带的permission系统只对模型有用，而不是针对某个具体的object。一旦用户获得编辑文档的权限，那么该用户将获得编辑所有文档的权限
@method_decorator(permission_required('app_blog.add_post', raise_exception=True), name='dispatch')
class ProductUpdate(UpdateView):
    ...

    def get_object(self, queryset=None):  # 通过get_object方法用户只能修改自己的的文档
        obj = super().get_object(queryset=queryset)
        if obj.author != self.request.user:
            raise Http404()
        return obj


'''
========================================================================
手动定义和分配权限(Permissions)
'''
# 有时django创建的4种可选权限满足不了我们的要求，这时我们需要自定义权限。
# 实现方法主要有两种。
# 下面我们将分别使用2种方法给 Post 模型新增了两个权限，一个是 publish_post, 一个是 comment_post。

# 方法1. 在 Mode l的 meta 属性中添加 permissions
class Post(models.Model):
    ...
    class Meta:
        permissions = (
            ("publish_post", "能发布文章"),
            ("comment_post", "能评论文章"),
        )


# 方法2. 使用 ContentType 程序化创建 permissions
from app_blog.models import Post
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

content_type = ContentType.objects.get_for_model(Post)
permission1 = Permission.objects.create(
    codename='publish_post',
    name='能发布文章',
    content_type=content_type,
)
permission2 = Permission.objects.create(
    codename='comment_post',
    name='能评论文章',
    content_type=content_type,
)
# 当你使用python manage.py migrate命令后，你会发现Django admin的user permissions栏又多了两个可选权限



'''
========================================================================
如果你不希望总是通过admin来给用户设置权限，你还可以在代码里手动给用户分配权限
'''
# 方法1. 使用 user.user_permissions.add() 方法
myuser.user_permissions.add(permission1, permission2, ...)
# 方法2. 通过user所在的用户组(group)给用户增加权限
mygroup.permissions.add(permission1, permission2, ...)


'''
========================================================================
如果你希望在代码中移除一个用户的权限，你可以使用remove或clear方法
'''
myuser.user_permissions.remove(permission, permission, ...)
myuser.user_permissions.clear()



'''
========================================================================
权限的缓存机制
'''
# Django会缓存每个用户对象，包括其权限user_permissions。
# 当你在代码中手动改变一个用户的权限后，你必须重新获取该用户对象，才能获取最新的权限。

# 比如下例在代码中给用户手动增加了change_blogpost的权限，如果不重新载入用户，那么将显示用户还是没有change_blogpost的权限。
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from app_blog.models import Post
 
def user_gains_perms(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    # 任何权限检查都将缓存当前权限集
    user.has_perm('app_blog.change_post') 

    # 添加权限
    content_type = ContentType.objects.get_for_model(Post)
    permission = Permission.objects.get(
        codename='change_post',
        name='能修改文章',
        content_type=content_type,
    )
    user.user_permissions.add(permission)  # 给用户新增权限

    # 检查缓存的权限集
    user.has_perm('app_blog.change_post')  # False

    # 请求用户的新实例
    # 请注意 user.refresh_from_db() 不会清除缓存。
    user = get_object_or_404(User, pk=user_id)

    # 从数据库重载权限缓存
    user.has_perm('app_blog.change_post')  # True


'''
========================================================================
用户组(Group)
'''

# 用户组(Group)和User模型是多对多的关系。
# 其作用在权限控制时可以批量对用户的权限进行管理和分配，而不用一个一个用户分配，节省工作量。
# 将一个用户加入到一个Group中后，该用户就拥有了该Group所分配的所有权限。
# 例如，如果一个用户组 editors 有权限 change_post , 那么所有属于 editors 组的用户都会有这个权限。

# 将用户添加到用户组或者给用户组(group)添加权限，一般建议直接通过django admin进行。
# 如果你希望手动给group添加或删除权限，你可以使用如下方法。

mygroup.permissions = [permission_list]
mygroup.permissions.add(permission, permission, ...)
mygroup.permissions.remove(permission, permission, ...)
mygroup.permissions.clear()
# 如果你要将某个用户移除某个用户组，可以使用如下方法。

myuser.groups.remove(group, group, ...) #
myuser.groups.clear()


# Django自带权限机制的不足
# Django自带的权限机制是针对模型的，这就意味着一个用户如果对Post模型有change的权限，那么该用户获得对所有文章对象进行修改的权限。
# 如果我们希望实现对单个文章对象的权限管理，我们需要借助于第三方库比如django guardian

