from uuid import uuid4

from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from .models import Article, Category, Comment


# 自定义 list_filter
class TitleKeywordFilter(admin.SimpleListFilter):
    #  右侧栏人为可读的标题
    title = '标题关键词'
    # 在url中显示的参数名，如?keyword=xxx.
    parameter_name = 'keyword'

    """
    自定义需要筛选的参数元组. 
    """
    def lookups(self, request, model_admin):
        return (
            ('python', '含python文章'),
            ('django', '含django文章'),
             )

    def queryset(self, request, queryset):
        """
        调用self.value()获取url中的参数， 然后筛选所需的queryset.
        """
        if self.value() == 'python':
            return queryset.filter(title__icontains='python')
        if self.value() == 'django':
            return queryset.filter(title__icontains='django')


# admin.site.register(Article, ArticleAdmin)  # 注册方式1
@admin.register(Article)  # 注册方式2（使用包装）
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['id', 'show_tags', 'title', 'author', 'created', 'publish', 'updated', 'status', 'is_delete', 'slug']  # 显示字段
    search_fields = ['title', 'body']  # 搜索字段
    list_filter = [TitleKeywordFilter, 'publish', 'created', 'updated', 'status']  # 过滤字段
    prepopulated_fields = {'slug':('title',)}  # 自动生成slug, 根据title填充slug
    raw_id_fields = ['author',]  # 下拉框改为微件(多个外键使建议使用)
    filter_horizontal = ['users_like']  # 多对多
    # filter_vertical = ['users_like']  # 多对多
    actions_on_top = True   # 执行动作的位置
    # actions_on_bottom = False
    ordering = ['author']  # 默认排序
    # fields = ['title', 'slug', 'author', 'body', 'publish', 'status']  # 在详细编辑页面的显示字段

    empty_value_display = '<span>-</span>'  # 字段值为空时显示的文本(可为纯文本,可为html)
    # admin_order_field = ('title', 'updated')  # 设置需要排序的字段
    list_per_page = 20  # 每页显示条目数
    list_editable = ('status', 'is_delete')  # 设置可编辑字段
    date_hierarchy = 'publish'  # 按日期月份筛选
    list_display_links = ['title', 'author']  # 设置带连接的字段

    actions = ['make_published', 'make_published_false', 
                'make_delete_true', 'make_delete_false', 
                'action_func']  # 自定义actions

    def make_published(self, request, queryset):
        # 注意: 此操作不会触发模型的 clean 方法!
        queryset.update(status='p', publish=timezone.now())
    make_published.short_description = "发布所选文章"
    make_published.allowed_permissions = ('change',)  #  要求只有change权限的管理人员才能更改文章发表状态

    def make_published_false(self, request, queryset):
        # 注意: 此操作不会触发模型的 clean 方法!
        queryset.update(status='d', publish=None)
    make_published_false.short_description = "取消发布"

    def make_delete_true(self, request, queryset):
        # 注意: 此操作不会触发模型的 clean 方法!
        queryset.update(is_delete=True)

    make_delete_true.short_description = "逻辑删除-是"

    def make_delete_false(self, request, queryset):
        # 注意: 此操作不会触发模型的 clean 方法!
        queryset.update(is_delete=False)

    make_delete_false.short_description = "逻辑删除-否"

    # 对批量选择进行某些操作
    # 如果想对queryset中的对象一个一个修改或导出
    def action_func(self, request, queryset):
        for obj in queryset:
            # do_something(obj)
            pass
    action_func.short_description = "对批量选择进行某些操作"

    # 重写了 get_actions 方法，只给了用户名为 891953720 批量删除对象的权限。
    # 如果用户名不为 891953720,我们把 delete_selected 动作从下拉菜单中删除
    def get_actions(self, request):
        actions = super().get_actions(request)
        if request.user.username != '891953720':
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions

    # 如果我们想实现根据不同的用户显示不同表单form，我们可以通过重写get_form方法实现。
    # 如下例中给Superuser显示了不同的表单
    # def get_form(self, request, obj=None, **kwargs):
    #     if request.user.is_superuser:
    #         kwargs['form'] = MySuperuserForm
    #     return super().get_form(request, obj, **kwargs)

    # 自定义显示表单的Choice字段
    # 下例中通过重写formfiled_for_choice_field方法给superuser多了一个选择
    # def formfield_for_choice_field(self, db_field, request, **kwargs):
    #     if db_field.name == "status":
    #         kwargs['choices'] = (
    #             ('accepted', 'Accepted'),
    #             ('denied', 'Denied'),
    #         )
    #         if request.user.is_superuser:
    #             kwargs['choices'] += (('ready', 'Ready for deployment'),)
    #     return super().formfield_for_choice_field(db_field, request, **kwargs)

    # model form 保存方法  (重写)
    # def save_model(self, request, obj, form, change):
    #     if form.is_valid():
    #         if not form.cleaned_data['slug']:
    #             obj.slug = uuid4().hex[:10]
    #         super().save_model(request, obj, form, change)

    # Django的admin默认会展示所有对象。
    # 通过重写get_queryset方法，我们可以控制所需要获取的对象。
    # 比如下例中，我们先对用户进行判定，如果用户是超级用户就展示所有文章，如果不是超级用户，我们仅展示用户自己所发表的文章
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)

    def show_tags(self, obj):
        '''展示tags'''
        tag_list = []
        tags = obj.tags.all()
        if tags:
            for tag in tags:
                tag_list.append(tag.name)
            return ','.join(tag_list)
        else:
            return format_html('<span style="color:red;">文章{}无标签</span>', obj.id,)
    show_tags.short_description = '标签'  # 设置表头


# admin.site.register(Category, CategoryAdmin)  # 注册方式1
@admin.register(Category)  # 注册方式2（使用包装）
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent_category', 'slug']
    prepopulated_fields = {'slug':('name',)}  # 自动生成slug, 根据name填充slug
    search_fields = ['name',]
    ordering = ['parent_category'] 


# admin.site.register(Comment)  # 注册方式1
@admin.register(Comment)  # 注册方式2（使用包装）
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'body', 'created', 'content_type', 'object_id', 'active']  # 显示字段
    search_fields = ['name', 'email', 'body']  # 搜索字段
    list_filter = ['created', 'active']  # 过滤器
    list_editable = ['active']
    # raw_id_fields = ['article',]  # 下拉框改为微件



