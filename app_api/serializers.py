from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueTogetherValidator

from app_blog.models import Article, Category
from app_user.models import UserProfile

User = get_user_model()

# REST framework 提供了 Serializer 类和 ModelSerializer 类两种方式来自定义序列化器


'''Serializer'''
class ArticleSerializer1(serializers.Serializer):
    '''
    read_only: 客户端是不需要也不能够通过POST或PUT请求提交相关数据进行反序列化.
    '''
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(required=True, allow_blank=True, max_length=90)
    body = serializers.CharField(required=False, allow_blank=True)
    author = serializers.ReadOnlyField(source="author.id")
    status = serializers.ChoiceField(choices=Article.STATUS_CHOICES, default='d')
    created = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        """
        创建新的 article 实例.
        """
        return Article.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        使用验证的数据更新并返回一个已存在的 article 实例.
        """
        instance.title = validated_data.get('title', instance.title)
        instance.body = validated_data.get('body', instance.body)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance


'''ModelSerializer'''
# 如果你希望author不可见并让DRF根据request.user自动补全这个字段
# class ArticleSerializer(serializers.ModelSerializer):
    # author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    # class Meta:
    #     model = Article
    #     fields = '__all__'
    #     read_only_fields = ('id', 'create_date')



# UserProfile
class UserProfileSerializer(serializers.ModelSerializer):
    '''UserProfile 序列化'''

    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ('id', 'uuid', 'created_time', 'last_mod_time', 'is_wanderer', 'user')

    def validate(self, data):
        errors = {}
        if not data.get('user', None):
            if not data['w_name']:
                errors['w_name'] = "不允未关联user的昵称为空!"
            if not data['w_email']:
                errors['w_email'] = "不允未关联user的邮箱为空!"
        if errors:
            raise serializers.ValidationError(errors)
        return data


# User
class UserSerializer(serializers.ModelSerializer):
    '''User 序列化'''

    # 关系序列化. NOTE: 'profile' ,'blog_articles' 必须为模型中定义的反向查询名称

    profile = UserProfileSerializer()  # 序列化器使用嵌套后,创建和更新的行为可能不明确,并且可能需要相关模型之间的复杂依赖关系,REST framework要求你始终显式的编写create和update方法.

    # profile = serializers.PrimaryKeyRelatedField(read_only=True)
    # blog_articles = serializers.PrimaryKeyRelatedField(many=True, read_only=True) # 以对应关系 model 的主键展现
    # blog_articles = serializers.StringRelatedField(many=True, read_only=True)     # 以对应关系 model 的 __str__() 形式展现

    # view_name 和 urls.py 中的 name 参数相对应，表示使用哪个 url, 果使用的是标准路由器类, 那么它的格式为 <model_name>-detail 的字符串
    # lookup_field 表示用哪个字段来作为 url 的唯一识别标记, 默认值为 pk.
    blog_articles = serializers.HyperlinkedRelatedField(                            # 自动生成一个 url 字段来表示超链接
        many=True,
        read_only=True,
        view_name='article-detail'
    )

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'blog_articles', 'profile')

    # 注册时提交的数据分别存入 User 和 UserProfile 模型
    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        user = User.objects.create(**validated_data)
        UserProfile.objects.create(user=user, **profile_data)
        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile')
        profile = instance.profile

        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.save()

        profile.photo = profile_data.get('photo', profile.photo)
        profile.telephone = profile_data.get('telephone', profile.telephone)
        profile.introduction = profile_data.get('introduction', profile.introduction)
        profile.save()

        return instance


# 分类
class CategorySerializer(serializers.ModelSerializer):
    '''分类序列化'''

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug')



def title_gt_90(value):
    if len(value) < 90:
        raise serializers.ValidationError('标题字符长度不低于90。')

# 文章
class ArticleSerializer(serializers.ModelSerializer):
    '''文章序列化'''

    # author = serializers.ReadOnlyField(source="author.username")  # 指定 author字段的来源 (source) 为单个 author 对象的 username

    # 使用嵌套序列化器, 显示更多用户对象信息, 或设置关联模型的深度depth(通常1-4). class Meta: depth=1
    # 使用嵌套序列化器时还需要重新指定一遍 read_only
    # required=False 表示可接受匿名用户, many=True表示有多个用户
    author = UserSerializer(read_only=True)

    # status = serializers.ReadOnlyField(source="get_status_display")  # 定义的字段会覆盖原来同名的字段
    full_status = serializers.ReadOnlyField(source="get_status_display")  # 新增 full_status 字段来显示完整的 status

    title = serializers.CharField(validators=[title_gt_90])  # 验证器 validators

    # 序列化日期和时间
    created = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S.%f", required=False, read_only=True)

    cn_status = serializers.SerializerMethodField()  # 将任何类型的数据添加到对象的序列化表
    # 该方法的命名为 get_ 加上要序列化的字段
    # 通常用于显示模型中原本不存在的字段
    def get_cn_status(self, obj):
        if obj.status == 'p':
            return "已发表"
        elif obj.status == 'd':
            return "草稿"
        else:
            return ''

    # 允许我们改变序列化的输出内容, 给其添加额外的数据
    def to_representation(self, instance):
        # 调用父类获取当前序列化数据
        data = super().to_representation(instance)
        # 对序列化数据做修改，添加新的数据
        data['total_likes'] = instance.users_like.count()  # 点赞总数
        return data

    # 字段级别验证 validate_<field_name>
    # NOTE: 如果在序列化器上声明了 <field_name> 的参数为 required=False,那么如果不包含该字段,则此验证步骤不会发生.
    def validate_title(self, value):
        if 'Carlos' not in value.lower():
            raise serializers.ValidationError("文章与Carlos无关.哈哈哈.出错咯!")
        return value

    # 对象级别验证
    def validate(self, data:dict):
        if data['updated'] > data['created']:
            raise serializers.ValidationError("出错啦, 哈哈哈哈!")
        return data

    class Meta:
        model = Article
        fields = '__all__'  # 所有字段 | 或指定的字段 fields = [title, body, ...]
        read_only_fields = ('id', 'author', 'created')
        # depth = 1  # 设置关联模型的深度, NOTE: 会展示关联模型中的所有字段.

        # 唯一性验证
        validators = UniqueTogetherValidator(
            queryset=Article.objects.all(),
            fields=['slug']
        )