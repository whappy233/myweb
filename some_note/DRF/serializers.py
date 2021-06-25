from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.parsers import JSONParser
from apps.app_blog.models import Article




'''
Seializer之间的继承关系:

                    django.db.models.fields.Field
                                ↑
                                |
                                |
                    rest_framework.serializers.BaseSerializer   ----→    定义 create, update 抽象方法
                                ↑
                                |
                                |
                    rest_framework.serializers.Serializer
                                ↑
                                |
                                |
                    rest_framework.serializers.ModelSerializer  ----→    重写 create, update


REST framework 提供了 Serializer 类和 ModelSerializer 类两种方式来自定义序列化器
'''




# ------------------------------------------------------------------------------------------------------------
# Serializer
# ------------------------------------------------------------------------------------------------------------
class ArticleSerializer(serializers.Serializer):
    '''
    read_only=True: 客户端是不需要也不能够通过POST或PUT请求提交相关数据进行反序列化, 前端只有读的权利.
    write_only=True 这个值让前端只会提交，不会再返回给前端，前端只有写的权利

    '''
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(required=True, allow_blank=True, max_length=90)
    body = serializers.CharField(required=False, allow_blank=True)

    # 控制serializer在某些情况下如何显示，比如渲染HTML的时候。
    # {'base_template': 'textarea.html'}标志等同于在 Django Form 类中使用widget=widgets.Textarea。
    # 这对于控制如何显示可浏览器浏览的API特别有用
    # body = serializers.CharField(required=False, allow_blank=True, style={'base_template': 'textarea.html'})

    author = serializers.ReadOnlyField(source="author.id")
    status = serializers.ChoiceField(choices=Article.STATUS_CHOICES, default='d')
    created = serializers.DateTimeField(read_only=True)


    def create(self, validated_data):
        """
        根据提供的验证过的数据创建并返回一个新的`Article`实例。
        """
        return Article.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        根据提供的验证过的数据更新和返回一个已存在的 Article 实例.
        """

        # validated_data 已经验证转换过的数据
        # init_data 原始的没有经过验证的数据
        instance.title = validated_data.get('title', instance.title)
        instance.body = validated_data.get('body', instance.body)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance


'''基本示例'''
# 序列化
article = Article(title='haha', body='xxxxxx', author=User.objects.first(), status='p')
article.save()
serialize = ArticleSerializer(article)  # 序列化单条数据
serialize.data # -> '{"id": 1, "title": "haha", "body": "xxxxxx"....}'

serializer = ArticleSerializer(Article.objects.all(), many=True)  # 序列化查询结果集
serializer.data

# 反序列化
import io
stream = io.BytesIO(content)
data = JSONParser().parse(stream)  # 首先将一个流（stream）解析为Python原生数据类型...
serializer = ArticleSerializer(data=data)
serializer.is_valid()
# True
serializer.validated_data
# OrderedDict([('title', 'aaa'), ('body', 'xxxxx'), ('status', 'p')...])
serializer.save()
# <Snippet: Snippet object>



# ------------------------------------------------------------------------------------------------------------
# ModelSerializer
# 该类并不会做任何特别神奇的事情，它们只是创建序列化器类(Serializer)的快捷方式：
#     一组自动确定的字段。
#     默认简单实现的create()和update()方法。
# ------------------------------------------------------------------------------------------------------------
class ArticleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Article
        fields = '__all__'  # 所有字段 | 或指定的字段 fields = [title, body, ...] 返回给前端的json中包含的字段
        read_only_fields = ('id', 'author', 'create_date')


# 如果你希望author不可见并让DRF根据request.user自动补全这个字段
class ArticleSerializer(serializers.ModelSerializer):
    # HiddenField 隐藏字段
    # serializers.CurrentUserDefault() 提取 request 中的 user
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())  

    class Meta:
        model = Article
        fields = '__all__'  # 所有字段 | 或指定的字段 fields = [title, body, ...] 返回给前端的json中包含的字段
        read_only_fields = ('id', 'create_date')


    # goods = serializers.SerializerMethodField()
    # # 自定义字段
    # # 该方法的命名为 get_ 加上要序列化的字段
    # def get_ad_goods(self, obj):
    #     print('get_ad_goods', obj.id)
    #     goods_json = {}
    #     # 这里传过来的只有'蔬菜水果','酒水饮料','粮油副食','生鲜食品'
    #     # 而他们的序号已经在IndexAd表中添加过了，所有会找到队友的商品纪录
    #     ad_goods = Category.objects.filter(category_id=obj.id, )
    #     if ad_goods:
    #         good_ins = ad_goods[0].goods
    #         # 在serializer的方法中使用Serializer的时候，他会检察上下文中有没有包含request,
    #         # 如果有，那么在返回的图片url中会自动加上域名 http://....
    #         # 如果没有，那么返回的url只会加上路径 /media/goods/images/......
    #         goods_json = GoodsSerializer(good_ins, many=False, context={'request': self.context['request']}).data
    #     return goods_json




