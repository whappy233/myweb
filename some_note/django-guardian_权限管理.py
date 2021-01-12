# =======================================================================================
# 1. 安装 
# pip install django-guardian


# =======================================================================================
# 2. 配置
# 添加到 App
INSTALLED_APPS = ( 
    # ... 
    'guardian',
)

# 加入到身份验证后端 AUTHENTICATION_BACKENDS
AUTHENTICATION_BACKENDS = ( 
    'django.contrib.auth.backends.ModelBackend', # 这是Django默认的
    'guardian.backends.ObjectPermissionBackend', # 这是guardian的
) 

# 创建guardian的数据库表
python manage.py migrate
# 当我们调用migrate命令将会创建一个匿名用户的实例（名为AnonymousUser ）。
# guardian 的匿名用户与 Django 的匿名用户不同。
# Django匿名用户在数据库中没有条目，但是Guardian匿名用户有。这意味着以下代码将返回意外的结果。
request.user.is_anonymous = True


# 额外设置
GUARDIAN_RAISE_403 = False
# 如果设置为True，guardian将会抛出 django.core.exceptions.PermissionDenied 异常，而不是返回一个空的 django.http.HttpResponseForbidden

GUARDIAN_RENDER_403 = False
# 如果 GUARDIAN_RENDER_403 设置为True, 将会尝试渲染403响应，而不是返回空的 django.http.HttpResponseForbidden.模板文件将通过 GUARDIAN_TEMPLATE_403 来设置。
# GUARDIAN_RENDER_403 和 GUARDIAN_RAISE_403 不能同时设置为True。否则将抛出django.core.exceptions.ImproperlyConfigured异常

ANONYMOUS_USER_NAME = 'AnonymousUser'
# 用来设置匿名用户的用户名，默认为 AnonymousUser。

GUARDIAN_GET_INIT_ANONYMOUS_USER = xxx
# Guardian支持匿名用户的对象级权限，但是在我们的项目中, 我们使用自定义用户模型，默认功能可能会失败。
# 这可能导致 guardian 每次 migrate 之后尝试创建匿名用户的问题。
# 将使用此设置指向的功能来获取要创建的对象。一旦获取，save方法将在该实例上被调用。

GUARDIAN_GET_CONTENT_TYPE = xxx
# 默认值为 guardian.ctypes.get_default_content_type
# Guardian 允许应用程序提供自定义函数以从对象和模型中检索内容类型。
# 当类或类层次结构以 ContentType 非标准方式使用框架时，这是有用的。
# 大多数应用程序不必更改此设置。
# 例如，当使用 django-polymorphic 适用于所有子模型的基本模型上的权限时，这是有用的。
# 在这种情况下，自定义函数将返回 ContentType 多态模型的基类和 ContentType 非多态类的常规模型。


# ========================================================================
# 3. 示例项目

# 3.1 假设我们有以下模型
from django.db import models
from django.contrib.auth.models import User
class Task(models.Model):
    summary = models.CharField(max_length=32)
    content = models.TextField()
    reported_by = models.ForeignKey(User)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        permissions = (
                ('view_task', 'View task'),
            )
# 当我们调用migrate命令的时候，view_task将会被添加到默认的权限集合中

# 3.2 分配对象权限
# 使用 guardian.shortcuts.assign_perm() 方法为用户/组分配对象权限
# 3.2.1 为用户分配权限
from django.contrib.auth.models import User
from guardian.shortcuts import assign_perm
boss = User.objects.create(username="Big Boss") # 创建用户的 boss
joe = User.objects.create(username="joe") # 创建用户joe
task = Task.objects.create(summary="Some job", content="", reported_by=boss) # 创建Task对象
assign_perm('view_task', joe, task) # 为用户joe分配权限

# 3.2.2 为用户组分配权限
from django.contrib.auth.models import Group
group = Group.objects.create(name="employees")
assign_perm("change_task", group, task)
jack = User.objects.create(username="jack")
jack.groups.add(group)


# 3.3 检查对象权限
# 3.3.1 标准方式
joe.has_perm('view_task', task)  # --> True or False

# 3.3.2 在视图中使用
from guardian.shortcuts import get_perms
'change_task' in get_perms(joe, task)  # --> True or False
# 建议尽量使用标准 has_perm 方法。
# 但是对于Group实例, 它不是那么容易, get_perms 解决这个问题很方便，因为它接受User和Group实例。
# 也可以使用 get_user_perms 获得直接分配权限给用户（而不是从它的超级用户权限或组成员资格继承的权限）。
# 同样的, get_group_perms 仅返回其是通过用户组的权限。

# 根据对象和权限获取用户  ---------------------------------------------------------------------
# get_users_with_perms  (get_groups_with_perms)
from guardian.shortcuts import get_users_with_perms
get_users_with_perms(task)
# <QuerySet [<User: zzz>, <User: xxx>, <User: ccc>]>  所有具有权限的用户

# 想让superuser用户也包含在内，可以设置参数with_superusers=True
get_users_with_perms(task, with_superusers=True)

# 要查看用户具有的权限，可以设置参数attach_perms=True
get_users_with_perms(task, with_superusers=True, attach_perms=True)
# {
#     <User: admin>: ['commontask_change', 'commontask_run', 'commontask_select'], 
#     <User: xxx>: ['commontask_run','commontask_select'], 
#     <User: ccc>: ['commontask_change', 'commontask_run'], 
#     <User: zzz>: ['commontask_select']
# }

# 如果我们仅想查看具有某个权限的用户，可以设置only_with_perms_in参数，例如我们只想查看对象所有具有commontask_change权限的用户
get_users_with_perms(task, with_superusers=True, only_with_perms_in=['commontask_change'])
# <QuerySet [<User: admin@163.com>, <User: qa@ops-coffee.cn>]>

# 默认情况下用户所数组如果具有权限的话也会返回，例如上边的我们把用户xxx加入到了group，
# 然后给group赋予了权限，那么用户也就具有了相应的权限，如果我们只想查看直接赋予用户的权限，
# 而并非间接通过group取得的权限用户列表，我们可以设置参数with_group_users=False，此参数默认为True
get_users_with_perms(task, with_superusers=True, with_group_users=False)


# 根据用户和权限获取对象  ---------------------------------------------------------------------
# get_objects_for_user  (get_objects_for_group)
from guardian.shortcuts import get_objects_for_user
get_objects_for_user(jack, 'app_name.change_task')  # --> <QuerySet [<Task: Task object>]>
get_objects_for_user(jack, 'app_name.view_task')  # --> <QuerySet []>
get_objects_for_user(jack, ['engine.commontask_run', 'engine.commontask_change'])

# 如果想要仅满足列表中的任意一个权限，可以添加第三个参数any_perm=True
get_objects_for_user(jack, ['engine.commontask_run', 'engine.commontask_change'], any_perm=True)

# ObjectPermissionChecker
# guardian.core.ObjectPermissionChecker 用于检查特定对象的用户/组的权限。
# 因为他缓存结果，因此我们可以在多次检查权限的代码的一部分中使用
from guardian.core import ObjectPermissionChecker
checker = ObjectPermissionChecker(joe)
checker.has_perm('view_task', task)  # --> True or False


# 使用装饰器  ---------------------------------------------------------------------
# django-guardian随附两个装饰器，这可能有助于简单的对象权限检查，
# 但请记住，在装饰视图被调用之前，这些装饰器会触发数据库——这意味着如果在视图中进行类似的查找，
# 那么最可能的一个（或更多，取决于查找）会发生额外的数据库查询。
from guardian.decorators import permission_required
from django.http import HttpResponse
@permission_required('engine.commontask_change')
def commontask_update_view(request):
    return HttpResponse('Hello')
# 当仅有一个权限参数时，则与django默认的permission_required装饰器无疑，表示用户是否具有整个model的commontask_change权限
# 但在guardian的permission_required装饰器还支持第二个参数，
# 参数类型为一个元组，类似这样(CommonTask, 'id', 'pk')，用来指定具体的对象，
# 其中CommonTask为model，id为model的字段，pk为view中用户传入的具体参数，id与pk为对应关系，
# 大概的查询逻辑就是CommonTask.objects.get(id=pk)，判断用户对此对象是否有CommonTask的权限，示例代码如下
@permission_required('engine.commontask_change', (CommonTask, 'id', 'pk'))
def commontask_delete_view(request, pk):
    if request.method == 'POST':
        try:
            _data = CommonTask.objects.get(id=int(pk))
            _data.delete()
            return JsonResponse({'state': 1, 'message': '删除成功!'})
        except Exception as e:
            return JsonResponse({'state': 0, 'message': 'Error: ' + str(e)})
    else:
        return JsonResponse({"state": 0, "message": "Request method '%s' not supported" % request.method.upper()})

# permission_required还接收以下几个参数：login_url、redirect_field_name、return_403、return_404、accept_global_perms，
# 其中 accept_global_perms 参数表示是否检查用户的全局权限，如果指定了特定对象，且设置了 accept_global_perms=False 则只检查对象权限，
# 不检查全局权限，accept_global_perms默认为False


# 3.3.3 在模板中使用
# {％ load  guardian_tags  ％}
# guardian.templatetags.guardian_tags.get_obj_perms(parser, token) 返回给定用户或者组和对象（Model实例）的权限列表。
'''
{% get_obj_perms request.user for flatpage as "flatpage_perms" %}
{% if "delete_flatpage" in flatpage_perms %}
<a href="/pages/delete?target={{ flatpage.url }}">Remove page</a>
{% endif %}
'''


# 3.4 移除对象权限
# 使用guardian.shortcuts.remove_perm()来移除权限
remove_perm("veiw_task", joe, task)  # --> (0, {'guardian.UserObjectPermission': 0})
# 以下例子会清除用户 zxcv 对 CommonTask 表下所有对象 engine.commontask_run 的权限
remove_perm('engine.commontask_run', User.objects.get(username='zxcv'), CommonTask.objects.all())
remove_perm('engine.commontask_run', User.objects.get(username='zxcv'))  # 与上面效果相同


# 3.5 孤儿对象许可
# 所谓孤儿许可，就是没用的许可。在大多数情况下，可能没啥事儿，但是一旦发生，后果有可能非常严重。
# Guardian 用来纪录某用户对某个模型对象有某个权限的纪录时是使用 UserObjectPermission 和 GroupObjectPermission 对象纪录的。
# 其中对于 object 的引用是 contenttype 对象（标示是那个模型类）和pk主键，对于用户则是对User表的外键引用。

# 比方说，有一个对象A。我们通过权限设置，设定joe用户对该对象有着编辑权限。
# 忽然有一天，用户joe被删除了。可想而知，我们分配而产生的UserObjectPermission对象仍然在数据库里面，记录着：joe 有对A的编辑权限。
# 又有一天，一个用户注册了一个用户，用户username为joe。因为之前的那个纪录，joe用户拥有对A的编辑权限。而此joe非彼joe，我们犯了一个大错误！

# 再比如说，当我们删除了某一个对象的时候，而这个对象的某种权限已经被赋予给某个用户，那么这个权限的纪录也就失效了。
# 如果什么时候和曾经删除过的对象是同一个模型类，而且主键和以前的那个相同，那么用户也就有可能对其本不应该拥有权限的对象有了权限。

# 因此，当我们删除 User 和相关的 Object 的时候，我们一定要删除其相关的所有 UserObjectPermission 和 GroupObjectPermission 对象。

# 解决办法，一个是显式编码，一个是通过其提供的自定义django命令：
1. 'python manage.py clean_orphan_obj_perms  '
2. "还有一个是定期调用 'guardian.utils.clean_orphan_obj_perms()'。该函数会返回删除的对象数目。"

# 在python的世界中，我们可以使用celery定期调度这个任务。
# 但是自定义命令和定期调度都不是合理的生产环境的解决办法。
# 要想真正解决，还是需要手动编码实现，最优雅的方式还是加上 
# post_delete signal给User或Object对象，关于对象的样例代码如下
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.db.models.signals import pre_delete
from guardian.models import UserObjectPermission
from guardian.models import GroupObjectPermission
from app_xxx.models import xxxModels
def remove_obj_perms_connected_with_user(sender, instance, **kwargs):
    filters = Q(content_type=ContentType.objects.get_for_model(instance), object_pk=instance.pk)
    UserObjectPermission.objects.filter(filters).delete()
    GroupObjectPermission.objects.filter(filters).delete()
pre_delete.connect(remove_obj_perms_connected_with_user, sender=xxxModels)