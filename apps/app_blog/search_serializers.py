'''
haystack 搜索相关
'''

from drf_haystack import serializers as HSER
from django.contrib.humanize.templatetags import humanize
from rest_framework import serializers
from itertools import chain
from .search_indexes import ArticleIndex
from .models import Article

from app_api.serializers import TagSerializer



'''

[
    {
        "object": {
            "title": "Django 第三方登录",
            "summary": "本章学习了通过django-allauth实更加麻烦一些...",
            "tags": [
                {
                    "name": "test",
                    "tag_url": "/tags/test/"
                },
                {
                    "name": "django",
                    "tag_url": "/tags/django/"
                }
            ],
            "detail_url": "/details/d031108bd0/",
            "category_url": "/categorys/cHl0aG9u/",
            "category_name": "python",
            "pub_time": "12小时之前"
        }
    }
]

'''



class ArticleSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)

    def to_representation(self, instance):
        '''改变序列化的输出内容, 给其添加额外的数据'''
        data = super().to_representation(instance)
        data['detail_url'] = instance.get_absolute_url()                       # 文章URL
        data['category_url'] = instance.category.get_absolute_url()     # 分类URL
        data['category_name'] = instance.category.name                  # 分类名
        data['pub_time'] = humanize.naturaltime(instance.pub_time)      # 时间人性化
        return data

    class Meta:
        model = Article
        fields = ('title', 'summary', 'tags')


class ArticleIndexSerializer(HSER.HaystackSerializer):

    object = ArticleSerializer(read_only=True)  # 只读,不可以进行反序列化

    # detail = serializers.HyperlinkedRelatedField(read_only=True, view_name='article-detail')

    # def to_representation(self, instance):
    #     '''改变序列化的输出内容, 给其添加额外的数据'''
    #     data = super().to_representation(instance)

    #     dd = ArticleSerializer(instance=instance.object, context=self.context).data.get('url', '')  # 文章URL
    #     data['url'] = dd
    #     return data


    class Meta:
        index_classes = [ArticleIndex]  # 索引类的名称,可以有多个
        # text 由索引类进行返回, object 由序列化类进行返回, 第一个参数必须是 text
        # 其他字段只有在 ArticleIndex 中定义过才会显示
        fields = ["text", "object", ]
        ignore_fields = ["text"]  # 忽略字段

        field_aliases = {
            "q": "text"   # text 的别名, /search/?q=xx <=> /search/?text=xx
        }

