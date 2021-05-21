# taggit 支持中文 slug


# 1. 在app 下创建文件 cn_taggit.py
from taggit.models import Tag, TaggedItem
from django.utils.text import slugify
class CnTag(Tag):
    class Meta:
        proxy = True

    def slugify(self, tag, i=None):
        return slugify(tag, allow_unicode=True)[:128]

class CnTaggedItem(TaggedItem):
    '''taggit 支持中文 slug'''
    class Meta:
        proxy = True

    @classmethod
    def tag_model(cls):
        return CnTag

# 2. app/models.py
# 文章模型
from django.db import models
from taggit.managers import TaggableManager
class Article(models.Model):
    '''文章模型'''
    tags = TaggableManager(blank=True, through=CnTaggedItem)  # 添加标签管理器
    ...

# 3. app/urls.py
from django.urls import re_path
from app import views
app_name = 'app_blog'  # 定义应用程序命名空间
urlpatterns = [
    re_path(r'^tags/(?P<tag_slug>.*)$', views.article_list, name='article_list_by_tag'),  # 某个标签下的所有文章

]

# 4. 迁移数据库
# python manage.py makemigrations
# python manage.py migrate