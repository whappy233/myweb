
'''select_related方法
select_related将会根据外键关系（注意: 仅限单对单和单对多关系)，
在执行查询语句的时候通过创建一条包含SQL inner join操作的SELECT语句来一次性获得主对象及相关对象的信息。
'''

# 当你查询单个主对象或主对象列表并需要在模板或其它地方中使用到每个对象的关联对象信息时，
# 请一定记住使用 select_related 和 prefetch_related 一次性获取所有对象信息，从而提升数据库查询效率，避免重复查询。

# 对与单对单或单对多外键ForeignKey字段，使用select_related方法
# 对于多对多字段和反向外键关系，使用prefetch_related方
# 两种方法均支持双下划线指定需要查询的关联对象的字段名
# 使用Prefetch方法可以给prefetch_related方法额外添加额外条件和属性。


from django.shortcuts import render
from app_blog.models import Article
from django.utils import timezone



# 在查询文章列表时同时一次性获取相关联的category对象信息，
# 这样在模板中调用 {{ article.category.name }}时就不用再查询数据库了。
def article_list(request):
    articles = Article.objects.all().select_related('category')
    return render(request, 'blog/article_list.html', {'articles': articles, })

# 获取id=13的文章对象同时，获取其相关category信息
Article.objects.select_related('category').get(id=13)

# 获取id=13的文章对象同时，获取其相关作者名字信息
Article.objects.select_related('author__name').get(id=13)

# 获取id=13的文章对象同时，获取其相关category和相关作者名字信息。下面方法等同。
Article.objects.select_related('category', 'author__name').get(id=13)
Article.objects.select_related('category').select_related('author__name').get(id=13)

# 使用select_related()可返回所有相关主键信息。all()非必需。
Article.objects.all().select_related()

# 获取 Article 信息同时获取blog信息。filter方法和selected_related方法顺序不重要。
Article.objects.filter(pub_date__gt=timezone.now()).select_related('blog')
Article.objects.select_related('blog').filter(pub_date__gt=timezone.now())
