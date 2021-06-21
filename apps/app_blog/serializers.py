from drf_haystack.serializers import HaystackSerializer

from .search_indexes import ArticleIndex
from app_api.serializers import ArticleSerializer
from app_blog.models import Article


class ArticleIndexSer(HaystackSerializer):

    # def to_representation(self, instance):
    #     # 注意这里的 instance.object 才是搜到的那个对象
    #     # (如果view里面的queryset是和rest-framework里的格式相同的话，instance才是搜到的那个对象)
    #     ret = super(ArticleIndexSer, self).to_representation(instance)
    #     if isinstance(instance.object, Article):
    #         ret["data"] = ArticleSerializer(instance=instance.object).data

    #     print(20*'+')
    #     print(ret['data'])

    #     return ret

    class Meta:
        index_classes = [ArticleIndex]
        fields = ["text", "title", "summary", "body"]
        # 这里可以写ignore_fields来忽略搜索那个字段
