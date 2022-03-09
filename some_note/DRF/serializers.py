from rest_framework import serializers, validators
from django.contrib.auth.models import User
from rest_framework.parsers import JSONParser
from apps.app_blog.models import Article

from django.utils.timezone import now


from app_api.serializers import UserProfileSerializer
from apps.app_user.models import UserProfile



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


# 字段参数
'''
# 选项参数:
max_length	        最大长度
min_lenght	        最小长度
allow_blank	        是否允许为空
trim_whitespace	    是否截断空白字符
max_value	        最小值
min_value	        最大值


# 通用参数:
read_only	        表明该字段仅用于序列化输出, 默认False
write_only	        表明该字段仅用于反序列化输入, 默认False
required	        表明该字段在反序列化时必须输入, 默认True
default	            反序列化时使用的默认值
allow_null	        表明该字段是否允许传入None, 默认False
validators	        该字段使用的验证器
error_messages	    包含错误编号与错误信息的字典
label	            用于HTML展示API页面时, 显示的字段名称
help_text	        用于HTML展示API页面时, 显示的字段帮助提示信息

'''


'''
=====================================================================================================================
Serializer
=====================================================================================================================
'''

def multiple_of_ten(value):
    if value % 10 != 0:
        raise serializers.ValidationError('Not a multiple of ten')

class ArticleSerializer(serializers.Serializer):
    '''
    read_only=True: 客户端是不需要也不能够通过POST或PUT请求提交相关数据进行反序列化, 前端只有读的权利.
    write_only=True 这个值让前端只会提交, 不会再返回给前端, 前端只有写的权利

    '''
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(required=True, allow_blank=True, max_length=90)
    body = serializers.CharField(required=False, allow_blank=True)

    # 各个字段都可以包含验证器
    score = serializers.IntegerField(validators=[multiple_of_ten])

    # 控制serializer在某些情况下如何显示, 比如渲染HTML的时候.
    # {'base_template': 'textarea.html'}标志等同于在 Django Form 类中使用widget=widgets.Textarea.
    # 这对于控制如何显示可浏览器浏览的API特别有用
    # body = serializers.CharField(required=False, allow_blank=True, style={'base_template': 'textarea.html'})

    author = serializers.ReadOnlyField(source="author.id")
    status = serializers.ChoiceField(choices=Article.STATUS_CHOICES, default='d')
    created = serializers.DateTimeField(read_only=True)

    class Meta:
        # 唯一性验证, 邮箱唯一
        validators = validators.UniqueTogetherValidator(
            queryset=User.objects.all(),
            fields=['email']
        )

    # 字段级别的验证: def validate_<field_name>(self, value): ...
    def validate_title(self, value):
        if 'django' not in value.lower():
            raise serializers.ValidationError("Blog post is not about Django")
        return value

    # 对象级别的验证(对多个字段进行校验), data: 字段值字典
    def validate(self, data):
        if data['created'] > now():
            raise serializers.ValidationError("创建时间竟然在未来!")
        if data['author'].username != 'Carlos':
            raise serializers.ValidationError("必须是我!")
        return data

    def create(self, validated_data):
        """
        根据提供的验证过的数据创建并返回一个新的`Article`实例.
        validated_data: 反序列化校验后的数据dict
        """

        return Article.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        根据提供的验证过的数据更新和返回一个已存在的 Article 实例.
        instance: 要修改的模型对象
        validated_data: 反序列化校验后的数据dict
        """

        # validated_data 已经验证转换过的数据
        # initial_data 原始的没有经过验证的数据
        instance.title = validated_data.get('title', instance.title)
        instance.body = validated_data.get('body', instance.body)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance


def 序列化():
    article = Article(title='haha', body='xxxxxx', author=User.objects.first(), status='p')
    article.save()
    # 
    serialize = ArticleSerializer(article)  # instance: 模型|查询集|字典. 序列化单条数据
    serialize.data # -> '{"id": 1, "title": "haha", "body": "xxxxxx"....}'
    # context 参数来传递任意的附加上下文
    serializer = ArticleSerializer(Article.objects.all(), many=True, context={'request': request})  # 序列化查询结果集
    serializer.data

def 反序列化_创建():
    import io
    stream = io.BytesIO('content')
    data = JSONParser().parse(stream)  # 首先将一个流（stream）解析为Python原生数据类型...
    serializer = ArticleSerializer(data=data)
    serializer.is_valid(raise_exception=False)  # => bool, raise_exception=True 直接抛出异常信息
    serializer.initial_data     # => 未修改的数据, 如果没有传递data关键字参数, 那么.initial_data属性就不存在
    serializer.validated_data   # => 已经验证转换过的数据(必须先调用 is_valid) OrderedDict([('title', 'aaa'), ('body', 'xxxxx'), ('status', 'p')...])
    serializer.save()           # => 如果创建序列化器对象的时, 没有传递instance实例, 则调用save()方法的时候, create()被调用, 相反, 如果传递了instance实例, 则调用save()方法的时候, update()被调用
    # 在对序列化器进行save()保存时, 可以额外传递数据, 这些数据可以在create()和update()中的validated_data参数获取到
    serializer.errors           # => 包含表示生成的错误消息的字典, {'email': [u'Enter a valid e-mail address.'], 'created': [u'This field is required.']}
    serializer.data

    # 默认序列化器必须传递所有 required=True 的字段, 否则会抛出验证异常。
    # 但是我们可以使用 partial 参数来允许部分字段在更新操作时可以不传,而使用原有的数据
    article = Article.objects.first()
    serializer = ArticleSerializer(article, data={'title': 'hello django', 'pub_date': article.pub_date})
    # 两种写法最终效果等价
    serializer = ArticleSerializer(article, data={'title': 'hello django'}, partial=True)

def 反序列化_更新():
    # 默认情况下, 序列化器必须传递所有必填字段的值, 否则就会引发验证错误。你可以使用 partial参数来允许部分更新。
    # 使用部分数据更新`comment` 
    serializer = ArticleSerializer(Article.objects.all(), data={'title': u'foo bar'}, partial=True)
    serializer.is_valid()
    serializer.initial_data
    serializer.validated_data
    serializer.save()
    serializer.data

def 关联对象嵌套序列化():
    # 如果关联的对象数据不是只有一个, 而是包含多个数据(一里面序列化多), 在声明关联字段时, 多补充一个 many=True 参数即可

    def P1_序列化器嵌套():
        # Serializer类本身也是一种Field, 并且可以用来表示一个对象类型嵌套在另一个对象中的关系。
        class UserSerializer(serializers.Serializer):
            email = serializers.EmailField()
            username = serializers.CharField(max_length=100)

        class CommentSerializer(serializers.Serializer):
            # 如果嵌套的关联字段可以接收一个列表, 那么应该将 many=True 标志传递给嵌套的序列化器
            # 如果嵌套表示可以接收 None 值, 则应该将 required=False 标志传递给嵌套的序列化器
            content = serializers.CharField(max_length=200)
            created = serializers.DateTimeField()
            user = UserSerializer()
        
        # {'content': 6, 'created': '2021-10-24', 'user': OrderedDict([('id', 2), ('btitle', '天龙八部'), ('image', None)])}

    def P2_PrimaryKeyRelatedField():
        '''此字段将被序列化为关联对象的主键ID'''
        hbook = serializers.PrimaryKeyRelatedField(label='图书', read_only=True)
        # 或
        hbook = serializers.PrimaryKeyRelatedField(label='图书', queryset=Article.objects.all())
        # 指明字段时需要包含read_only=True或者queryset参数:
        #   包含read_only=True参数时, 该字段将不能用作反序列化使用
        #   包含queryset参数时, 将被用作反序列化时参数校验使用

        # {'id': 6, 'hname': '乔峰', 'hgender': 1, 'hcomment': '降龙十八掌', 'hbook': 2}

    def P3_StringRelatedField():
        '''此字段将被序列化为关联对象的字符串表示方式（即__str__方法的返回值）'''
        hbook = serializers.StringRelatedField(label='图书')

        # {'id': 6, 'hname': '乔峰', 'hgender': 1, 'hcomment': '降龙十八掌', 'hbook': '天龙八部'}





'''
=====================================================================================================================
模型类序列化器 ModelSerializer
=====================================================================================================================

该类只是创建序列化器类(Serializer)的快捷方式：
    它根据模型自动生成一组字段.
    它自动生成序列化器的验证器, 比如unique_together验证器.
    它默认简单实现了.create()方法和.update()方法.

'''

# 为嵌套关系定义.create()方法
class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()  # 将得到关联对象的所有字段 OrderDict

    class Meta:
        model = User
        fields = ('username', 'email', 'profile')

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        user = User.objects.create(**validated_data)
        UserProfile.objects.create(user=user, **profile_data)
        return user

# 为嵌套关系定义.update()方法
# 对于更新, 你需要仔细考虑如何处理关联字段的更新。例如, 如果关联字段的值是None, 或者没有提供, 那么会发生下面哪一项？
#   在数据库中将关联字段设置成NULL。
#   删除关联的实例。
#   忽略数据并保留这个实例。
#   抛出验证错误。
class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ('username', 'email', 'profile')

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile')
        # 除非应用程序正确执行, 
        # 保证这个字段一直被设置, 
        # 否则就应该抛出一个需要处理的`DoesNotExist`。
        profile = instance.profile

        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.save()

        profile.is_premium_member = profile_data.get(
            'is_premium_member',
            profile.is_premium_member
        )
        profile.has_support_contract = profile_data.get(
            'has_support_contract',
            profile.has_support_contract
         )
        profile.save()

        return instance


class ArticleSerializer(serializers.ModelSerializer):

    # 声明字段来增加额外的字段(对应模型上任何属性或可调用的方法)或者重写默认的字段
    url = serializers.CharField(source='get_absolute_url', read_only=True)  # get_absolute_url 模型上可调用的方法

    # 关联外键字段
    # user_likes = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())  # 外键字段(id), many多个对象, queryset 表明在更新groups 时的数据必须是User.objects.all()中的对象
    # user_likes = serializers.StringRelatedField(many=True, queryset=User.objects.all())  # 外键字段(__str__), many多个对象, queryset 表明在更新groups 时的数据必须是User.objects.all()中的对象
    # user_likes = UserSerializer(many=True, queryset=User.objects.all()) 

    class Meta:
        model = Article
        fields = '__all__'                  # 所有字段 | 或指定的字段 fields = (title, body, ...) 返回给前端的json中包含的字段
                                            # fields 选项中的名称可以映射到模型类中的 '模型字段'和 '不存在任何参数的属性或方法'
        exclude = ('id', 'title', )         # 从序列化器中排除的字段 映射到模型类中的 '模型字段'
        read_only_fields = ('id', 'author') # 指定只读字段
        depth = 1                           # 遍历的关联深度
        extra_kwargs = {                    # 添加或修改原有的选项参数
            'views': {'max_length': 2000, 'required': True},
            'created': {'write_only': True}
        }


# 如果你希望author不可见并让DRF根据request.user自动补全这个字段
class ArticleSerializer(serializers.ModelSerializer):
    # HiddenField 隐藏字段
    # serializers.CurrentUserDefault() 提取 request 中的 user
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())  

    class Meta:
        model = Article
        fields = '__all__'  
        read_only_fields = ('id', 'create_date')


    # goods = serializers.SerializerMethodField()
    # # 自定义字段
    # # 该方法的命名为 get_ 加上要序列化的字段
    # def get_ad_goods(self, obj):
    #     print('get_ad_goods', obj.id)
    #     goods_json = {}
    #     # 这里传过来的只有'蔬菜水果','酒水饮料','粮油副食','生鲜食品'
    #     # 而他们的序号已经在IndexAd表中添加过了, 所有会找到队友的商品纪录
    #     ad_goods = Category.objects.filter(category_id=obj.id, )
    #     if ad_goods:
    #         good_ins = ad_goods[0].goods
    #         # 在serializer的方法中使用Serializer的时候, 他会检察 context 中有没有包含request,
    #         # 如果有, 那么在返回的图片url中会自动加上域名 http://....
    #         # 如果没有, 那么返回的url只会加上路径 /media/goods/images/......
    #         goods_json = GoodsSerializer(good_ins, many=False, context={'request': self.context['request']}).data
    #     return goods_json



'''
=====================================================================================================================
HyperlinkedModelSerializer
=====================================================================================================================
类似于 ModelSerializer 类, 不同之处在于它使用超链接来表示关联关系而不是主键。
    默认情况下序列化器将包含一个 url 字段而不是主键字段。
    url 字段将使 用HyperlinkedIdentityField 字段来表示, 
    模型的任何关联都将使用 HyperlinkedRelatedField 字段来表示。
'''
class AccountSerializer(serializers.HyperlinkedModelSerializer):

    url = serializers.HyperlinkedIdentityField(
        view_name='accounts',
        lookup_field='slug'
    )
    users = serializers.HyperlinkedRelatedField(
        view_name='user-detail',
        lookup_field='username',
        many=True,
        read_only=True
    )

    class Meta:
        model = Article
        fields = ('url', 'id', 'account_name', 'users', 'created')

        # 默认情况下, 超链接期望对应到一个样式能匹配'{model_name}-detail'的视图, 并通过pk关键字参数查找实例
        # 你可以通过在extra_kwargs中设置view_name和lookup_field中的一个或两个来重写URL字段视图名称和查询字段
        # 或者你可以显式的设置序列化器上的字段, 见类属性 url, users
        # extra_kwargs = {
        #     'url': {'view_name': 'accounts', 'lookup_field': 'account_name'},
        #     'users': {'lookup_field': 'username'}
        # }


# 当实例化一个HyperlinkedModelSerializer时, 你必须在序列化器的上下文中包含当前的request值, 确保超链接可以包含恰当的主机名
# 如果你真的要使用相对URL, 你应该明确的在序列化器上下文中传递一个{'request': None}
serializer = AccountSerializer(Article.objects.all(), context={'request': request})








