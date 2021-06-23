'''
haystack 搜索相关
'''

from drf_haystack import serializers as HSER
from rest_framework import serializers
from itertools import chain
from .search_indexes import ArticleIndex
from .models import Article



class ArticleSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        '''改变序列化的输出内容, 给其添加额外的数据'''
        data = super().to_representation(instance)
        data['url'] = instance.get_absolute_url()  # 文章URL
        return data

    class Meta:
        model = Article
        fields = ('title', 'summary', 'url',)


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

