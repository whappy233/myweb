
# Django ContentTypes是一个非常有用的框架，主要用来创建模型间的通用关系(generic relation).

# Django ContentTypes框架使用场景
# 假设我们创建了如下模型，里面包含文章Article，Picture和评论Comment模型。
# Comment可以是对Article的评论，也可以是对Picture的评论。
# 如果你还想对其它对象（比如回答，用户) 进行评论, 这样你将需要在comment对象里添加非常多的ForeignKey。
# 你的直觉会告诉你，这样做很傻，会造成代码重复和字段浪费。
# 一个更好的方式是，只有当你需要对某个对象或模型进行评论时，才创建comment与那个模型的关系。
# 这时你就需要使用 django contenttypes了



from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation

class Article(models.Model):
    author = models.ForeignKey(User)
    title = models.CharField(max_length=75)
    body = models.TextField(blank=True)
    comments = GenericRelation('Comment')  # 该字段不会存储于数据库中


class Picture(models.Model):
    author = models.ForeignKey(User)
    image = models.ImageField()
    caption = models.TextField(blank=True)
    comments = GenericRelation('Comment')  # 该字段不会存储于数据库中


class Comment(models.Model):
    author = models.ForeignKey(User)
    body = models.TextField(blank=True)
    content_type = models.ForeignKey(ContentType)  # 内容类型，代表了模型的名字(比如Article, Picture)
    object_id = models.PositiveIntegerField()  # 传入对象的id
    content_object = GenericForeignKey()  # 传入的实例化对象，其包含两个属性content_type和object_id



# 注意
# 如果在Article中定义了GenericRelation，删除了一个article实例，在Comment中所有与article相关实例也会被删除。
# GenericForeignKey不支持设置on_delete参数。 
# 因此，如果对级联删除不满意的话就不要设置 GenericRelation


# 1. 在不设置 GenericRelation 的情况下, 按如下代码建立评论关系。
user = User.objects.get(username='user1')
article = Article.objects.get(title='title1')
c = Comment.objects.create(author=user, body='', content_object=article)
picture = Picture.objects.get(caption='picuture1')
c1 = Comment.objects.create(author=user, body='', content_object=picture)

# 2. 在设置 GenericRelation 的情况下
me = User.objects.get(username='myusername')
pic = Picture.objects.get(author=me)
pic.comments.create(author=me, body="Man, I'm cool!")
pic.comments.all() # --> [<Comment: "Man, I'm cool!">]