from uuid import uuid4

from app_user.models import UserProfile
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from django.core import serializers
from mdeditor.fields import MDTextField  # 富文本编辑器 mdeditor




def uuid4_hex():
    return uuid4().hex


# 自定义 Comments 管理器. 在默认管理器上增加方法
class ModelManager(models.Manager):

    def invisible_count(self):
        '''不可见评论的数量'''
        hidden = set()
        h = self.filter(is_hide=True)
        for commnet in h:
            hidden.update(commnet.get_all_children())
        return len(hidden)

    def visible_count(self):
        '''可见评论的数量'''
        return self.count() - self.invisible_count()

    def visible_comments(self, start=None, end=None, serialize=False, fields=None, **kwargs):
        '''可见评论'''
        data = []
        h = self.filter(is_hide=False, parent_comment=None, **kwargs)[start:end]
        for commnet in h:
            data.extend(commnet.get_show_children(serialize, fields))
        return data


# 评论模型
class Comments(models.Model):
    '''评论模型'''

    body = MDTextField('评论内容')
    uuid = models.CharField('唯一标识', max_length=32,
                            unique=True, default=uuid4_hex, editable=False)

    # user_obj.comments.all() 某 user 下的所有评论
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE,
                               related_name='comments',
                               blank=True, null=True,
                               verbose_name='评论作者')

    # comment_obj.child_comments.all() 某评论下的所有子评论
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE,
                                       related_name='child_comments',
                                       blank=True, null=True,
                                       db_index=True,
                                       verbose_name="上级评论")

    ip_address = models.GenericIPAddressField('IP地址', unpack_ipv4=True, blank=True, null=True)
    is_overhead = models.BooleanField('是否顶置', default=False)
    is_hide = models.BooleanField('是否隐藏', default=False)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)

    # 使用admin呈现此字段时，设置对此字段(limit_choices_to)的可用选项的限制(默认情况下, 查询集中的所有对象都可供选择).
    # 可以使用字典、Q对象或可调用返回字典或Q对象.
    # step1 内容类型，代表了模型的名字(比如Article, Picture)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                                     limit_choices_to={
                                        "model__in": ("article", 'photo')
                                     },
                                     verbose_name='关联对象类型')
    # step2 传入对象的id
    object_id = models.PositiveIntegerField('关联对象ID')
    # step3 传入的实例化对象，其包含两个属性content_type和object_id
    content_object = GenericForeignKey('content_type', 'object_id')

    objects = ModelManager()

    class Meta:
        ordering = ('-is_overhead', '-created_time')
        verbose_name = '评论'
        verbose_name_plural = verbose_name

    def to_serialize(self, fields=None):
        data = serializers.serialize("json", [self], fields=fields, use_natural_foreign_keys=True)[0]
        return data

    def get_all_parents(self):
        '''获取所有父级'''
        parents = [self]
        if self.parent_comment is not None:
            parent = self.parent_comment
            parents.extend(parent.get_all_parents())
        return parents

    def get_all_children(self):
        '''获取所有子级'''
        children = [self]
        try:
            child_list = self.child_comments.all()
        except AttributeError:
            return children
        for child in child_list:
            children.extend(child.get_all_children())
        return children

    def get_show_children(self, serialize=False, fields=None):
        show = []
        if self.is_hide:
            return []
        else:
            if serialize:
                show.append(self.to_serialize(fields))
            else:
                show.append(self)
        try:
            child_list = self.child_comments.filter(is_hide=False)
        except AttributeError:
            return show
        for child in child_list:
            show.extend(child.get_show_children(serialize, fields))
        return show

    def clean(self):
        if self.parent_comment in self.get_all_children():
            raise ValidationError("不能将自己或其子级之一作为父级.")

        if self.parent_comment:
            p_obj_type = type(self.parent_comment.content_object)
            curr_obj_type = type(self.content_object)
            if p_obj_type != curr_obj_type:
                raise ValidationError(
                    '父评论关联对象类型与新建评论的关联对象类型应该相同. 父评论关联对象:'
                    f'"{self.parent_comment.content_object._meta.verbose_name}"'
                    f', 当前评论关联对象: "{self.content_type}"')

    def save(self, *args, **kwargs):
        if self.is_overhead == True and self.parent_comment:
            raise ValueError('不允许顶置非顶级评论')

        super().save(*args, **kwargs)

    def __str__(self):
        return f'ID: {self.id}-{self.body[:10]}... ({self.content_type}ID: {self.object_id})'

    def natural_key(self):
        return {'uuid': self.uuid, 'author_uuid': self.author.uuid, 'username': self.author.username}


class MpComments(MPTTModel):

    body = models.TextField('评论内容', max_length=500)
    uuid = models.CharField('唯一标识', max_length=32, unique=True, default=uuid4_hex, editable=False)

    # user_obj.comments.all() 某 user 下的所有评论
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE,
                               related_name='mp_comments',
                               blank=True, null=True,
                               verbose_name='评论作者')

    # 上级评论 (parent 为默认字段, 如要修改则在 MPTTMeta 中修改 parent_attr='parent')
    parent_comment = TreeForeignKey('self', on_delete=models.CASCADE,
                                    related_name='child_comments',
                                    blank=True, null=True,
                                    db_index=True,
                                    verbose_name="上级评论")

    # # 记录二级评论回复给谁, str
    # reply_to = models.ForeignKey(UserProfile, on_delete=models.CASCADE,
    #                             blank=True,null=True,
    #                             related_name='replyers')

    ip_address = models.GenericIPAddressField('IP地址', unpack_ipv4=True, blank=True, null=True)
    is_overhead = models.BooleanField('是否顶置', default=False)
    is_hide = models.BooleanField('是否隐藏', default=False)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)

    # 使用admin呈现此字段时，设置对此字段(limit_choices_to)的可用选项的限制(默认情况下, 查询集中的所有对象都可供选择).
    # 可以使用字典、Q对象或可调用返回字典或Q对象.
    # step1 内容类型，代表了模型的名字(比如Article, Picture)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                                     limit_choices_to={"model__in": ("article", 'photo')},
                                     verbose_name='关联对象类型')
    # step2 传入对象的id
    object_id = models.PositiveIntegerField('关联对象ID')
    # step3 传入的实例化对象，其包含两个属性content_type和object_id
    content_object = GenericForeignKey('content_type', 'object_id')

    class MPTTMeta:
        parent_attr = 'parent_comment'
        order_insertion_by = ['-is_overhead', '-created_time']

    def __str__(self):
        hide = '❌'if self.is_hide else '✅'
        return f'ID: {self.id}-{self.body} {hide} ({self.content_type}ID: {self.object_id})'


# 隐藏的评论数
# MpComments.objects.filter(is_hide=True).get_descendants(True).count()


# MpComments.objects.filter(parent=None, is_hide=False).get_descendants(True)  # good
# MpComments.objects.filter(is_hide=False).get_descendants(True)  # bad


'''
要显示的评论
1. 
a = MpComments.objects.values_list('tree_id','created_time', 'body')
b = MpComments.objects.filter(is_hide=True).get_descendants(True).values_list('tree_id', 'created_time','body')
x = set(a)^set(b)

2.
b = MpComments.objects.filter(is_hide=True).get_descendants(True).values_list('pk')
show = MpComments.objects.exclude(pk__in=list(zip(*b))[0])
'''


# mp = MpComments()

'''创建一个包含此模型实例祖先的 QuerySet.  所有祖先
ascending 默认情况是按降序排列(根祖先第一, 直接父母最后).
如果include_self为True，则QuerySet也将包含此模型实例.
如果实例还没有保存，则ValueError.'''
# mp.get_ancestors(ascending=False, include_self=False)

'''创建包含模型实例的后代的 QuerySet.  所有后代
如果include_self为True，则QuerySet也将包含此模型实例.
如果实例还没有保存，则ValueError.'''
# mp.get_descendants(include_self=False)

'''创建一个包含此模型实例的同级元素的QuerySet。 根节点被认为是其他根节点的兄弟节点。 所有同级
如果include_self为True，则QuerySet也将包含此模型实例.
如果实例还没有保存，则ValueError.'''
# mp.get_siblings(include_self=False)

'''返回包含祖先，模型本身和后代的 QuerySet  所有一家子.
如果实例还没有保存，则ValueError.'''
# mp.get_family()

'''返回包含此模型实例的直接子级的 QuerySet. 亲儿子
如果实例还没有保存，则ValueError.'''
# mp.get_children()

'''根据模型实例的左、右树节点边缘指示器，返回其后代数量。不会产生任何数据库访问'''
# mp.get_descendant_count()

'''返回树中该模型实例的下一个同级, 如果没有下一个同级,则返回None.
如果实例还没有保存，则ValueError.'''
# mp.get_next_sibling()

'''返回树中该模型实例的上一个同级, 如果没有上一个同级,则返回None.
如果实例还没有保存，则ValueError.'''
# mp.get_previous_sibling()

'''返回根节点
如果实例还没有保存，则ValueError.'''
# mp.get_root()

'''如果模型实例是子节点, 返回 True'''
# mp.is_child_node()

'''如果模型实例是叶节点(它没有孩子), 返回 True'''
# mp.is_leaf_node()

'''如果模型实例是根节点, 返回 True'''
# mp.is_root_node()


'''根据 target 和 position(在适当的情况下), 将模型实例(必须尚未插入数据库中)放置在树中.
如果save为True，还将调用模型实例的save()方法.'''
# mp.insert_at(target, position='first-child', save=False, allow_existing_pk=False, refresh_target=True)


'''根据 target 和 position(适当时), 将模型实例移动到树中的其他位置.
如果移动时没有引发任何异常，则将发送 node_moved 信号.

如果 target 是另一个模型实例，它将与位置参数position一起用于确定需要进行的移动类型，并用作模型移动时对模型进行定位的基础.
target=None 表示应将模型实例转换为根节点.在这种情况下,忽略position参数.

position 参数及其对运动的影响的有效值为：
'firdt-child': 要移动的实例应将目标设置为其新的父对象，并作为其第一个子对象放置在树结构中。
'firdt-child': 要移动的实例应将目标设置为其新的父对象，并作为其最后一个子对象放置在树结构中。
'left': 要移动的实例应将目标的父级设置为新的父级，并应将其直接放置在树形结构中目标之前。
'right': 要移动的实例应将目标的父级设置为新的父级，并应将其直接放置在树形结构中目标之后。
如果为position参数指定了无效值，则会引发ValueError。

NOTE: 假定调用此方法时，调用它的实例中的树字段以及传入的任何目标实例(target)中的树字段均反映数据库的当前状态.
在调用此方法之前手动修改树字段或使用与数据库不同步的树字段可能会导致树结构处于不正确的状态.

NOTE: 使用此方法进行的某些移动是无效的-例如，尝试使实例成为其自己的子代或其子代之一的子代。 在这些情况下，将引发 mptt.exceptions.InvalidMove 异常。
调用后，实例本身也将被修改，以反映其更新的树字段在数据库中的状态，因此，在调用此方法后，可以继续保存实例或使用其树字段。 
'''
# mp.move_to(target, position='firdt-child')
