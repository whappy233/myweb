
'''
prefect_related
对于多对多字段，你不能使用 select_related 方法，这样做是为了避免对多对多字段执行JOIN操作从而造成最后的表非常大。
Django提供了 prefect_related 方法来解决这个问题。
prefect_related 可用于多对多关系字段，也可用于反向外键关系(related_name)。
'''

# 当你查询单个主对象或主对象列表并需要在模板或其它地方中使用到每个对象的关联对象信息时，
# 请一定记住使用 select_related 和 prefetch_related 一次性获取所有对象信息，从而提升数据库查询效率，避免重复查询。

# 对与单对单或单对多外键ForeignKey字段，使用select_related方法
# 对于多对多字段和反向外键关系，使用prefetch_related方
# 两种方法均支持双下划线指定需要查询的关联对象的字段名
# 使用Prefetch方法可以给prefetch_related方法额外添加额外条件和属性。


from django.db.models.query import Prefetch
from django.shortcuts import render
from app_blog.models import Post
from taggit.managers import TaggableManager

def post_list(request):
    posts = Post.objects.all().select_related('category').prefetch_related('tags')
    return render(request, 'blog/post_list.html', {'posts': posts, })


# 文章列表及每篇文章的tags对象名字信息
Post.objects.all().prefetch_related('tags__name')

# 获取id=13的文章对象同时，获取其相关tags信息
Post.objects.prefetch_related('tags').get(id=13)



# 现在问题来了，如果我们获取tags对象时只希望获取以字母P开头的tag对象怎么办呢？
# 我们可以使用Prefetch方法给prefect_related方法添加条件和属性。

# 获取文章列表及每篇文章相关的名字以P开头的tags对象信息
Post.objects.all().prefetch_related(
    Prefetch('tags', queryset=TaggableManager.objects.filter(name__startswith="P"))
)

# 文章列表及每篇文章的名字以P开头的tags对象信息, 放在post_p_tag列表
Post.objects.all().prefetch_related(
    Prefetch('tags', queryset=TaggableManager.objects.filter(name__startswith="P")),
to_attr='post_p_tag'
)