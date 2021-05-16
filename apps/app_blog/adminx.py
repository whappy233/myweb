from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from xadmin.sites import register

from .cn_taggit import CnTag
from .models import Article, Category


class ShortDescriptionMixin:

    # 链接到用户信息 xadmin/auth/user/1/update/
    def user_info(self, obj):
        info = (obj.author._meta.app_label, obj.author._meta.model_name)
        link = reverse('xadmin:%s_%s_change' % info, args=(obj.author.id,))
        return format_html(f'<a href="{link}">{obj.author.username}</a>')
    user_info.short_description = '作者'

    # 链接到分类信息 /xadmin/app_blog/category/1/update/
    def category_info(self, obj):
        info = (obj.category._meta.app_label, obj.category._meta.model_name)
        link = reverse('xadmin:%s_%s_change' % info, args=(obj.category.id,))
        return format_html(f'<a href="{link}">{obj.category.name}</a>')
    category_info.short_description = '分类'

    # 连接到标签信息 /xadmin/taggit/tag/4/update/
    def tag_info(self, obj):
        tag_list = []
        tags = obj.tags.all()
        for tag in tags:
            # ('app_blog', 'cntag')
            info = (tag._meta.app_label, tag._meta.model_name)
            link = reverse('xadmin:%s_%s_change' % info, args=(tag.id,))
            tag_list.append(f'<a href="{link}">{tag.name}</a>')
        return format_html(', '.join(tag_list))
    tag_info.short_description = '标签'

    def detail_view(self, obj):
        link = reverse('app_blog:article_detail', args=(obj.slug,))
        return format_html(f'<a href="{link}">👀</a>')
    detail_view.short_description = '预览'


    # ACTION -------------------------------------
    def make_published(self, request, queryset):
        # 注意: 此操作不会触发模型的 clean 方法!
        queryset.update(status='p', pub_time=timezone.now())
    make_published.short_description = "发布所选文章"
    make_published.allowed_permissions = ('change',)  #  要求只有change权限的管理人员才能更改文章发表状态

    def make_published_false(self, request, queryset):
        # 注意: 此操作不会触发模型的 clean 方法!
        queryset.update(status='d', pub_time=None)
    make_published_false.short_description = "取消发布"

    def make_delete_true(self, request, queryset):
        # 注意: 此操作不会触发模型的 clean 方法!
        queryset.update(is_delete=True)
    make_delete_true.short_description = "逻辑删除-是"

    def make_delete_false(self, request, queryset):
        # 注意: 此操作不会触发模型的 clean 方法!
        queryset.update(is_delete=False)
    make_delete_false.short_description = "逻辑删除-否"

    def close_article_commentstatus(self, request, queryset):
        queryset.update(comment_status='c')
    close_article_commentstatus.short_description = '关闭文章评论'

    def open_article_commentstatus(self, request, queryset):
        queryset.update(comment_status='o')
    open_article_commentstatus.short_description = '打开文章评论'

    # 对批量选择进行某些操作. 如果想对queryset中的对象一个一个修改或导出
    def action_func(self, request, queryset):
        for obj in queryset:
            # do_something(obj)
            pass
    action_func.short_description = "对批量选择进行某些操作"



# 文章
# xadmin.site.register(Article, ArticleAdmin)  # 注册方式1
@register(Article)  # 注册方式2
class ArticleAdmin(ShortDescriptionMixin):
    list_display = ['id', 'tag_info', 'category_info', 'user_info', 'detail_view',
                    'title', 'created', 'pub_time', 'updated',
                    'status', 'is_delete', 'slug', 'comment_status']  # 显示字段

    search_fields = ['title', 'body']  # 搜索字段

    list_filter = ['pub_time', 'created', 'updated', 'status', 'tags', 'category__name']  # 过滤字段

    prepopulated_fields = {'slug':('title',)}  # 自动生成slug, 根据title填充slug

    raw_id_fields = ['author',]  # 下拉框改为微件(多个外键使建议使用)

    filter_horizontal = ['users_like']  # 多对多

    # filter_vertical = ['users_like']  # 多对多

    actions_on_top = True   # 执行动作的位置
    # actions_on_bottom = False

    ordering = ['created']  # 默认排序

    # fields = ['title', 'slug', 'author', 'body', 'status']  # 在详细编辑页面的显示字段

    empty_value_display = '<span>-</span>'  # 字段值为空时显示的文本(可为纯文本,可为html)

    # admin_order_field = ('title', 'updated')  # 设置需要排序的字段

    list_per_page = 20  # 每页显示条目数

    list_editable = ('status', 'is_delete', 'comment_status')  # 设置可编辑字段

    date_hierarchy = 'pub_time'  # 按日期月份筛选

    list_display_links = ['title']  # 设置带连接的字段, 连接到updata 页面

    actions = ['make_published', 'make_published_false', 'make_delete_true',
                'make_delete_false', 'action_func', 'close_article_commentstatus',
                'open_article_commentstatus']  # 自定义actions

    # 重写了 get_actions 方法，只给了用户名为 891953720 批量删除对象的权限。
    # 如果用户名不为 891953720,我们把 delete_selected 动作从下拉菜单中删除
    def get_actions(self, request):
        actions = super().get_actions(request)
        if request.user.username != '891953720':
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions

    # xadmin根据当前登录用户动态设置表单字段默认值方式
    # 需要重写instance_forms方法，此方法作用是生成表单实例
    def instance_forms(self):
        super().instance_forms()
        # 判断是否为新建操作，新建操作才会设置creator的默认值
        if not self.org_obj:
            self.form_obj.initial['author'] = self.request.user.id

    # 如果我们想实现根据不同的用户显示不同表单form，我们可以通过重写get_form方法实现。
    # 如下例中给Superuser显示了不同的表单
    # def get_form(self, request, obj=None, **kwargs):
    #     if request.user.is_superuser:
    #         kwargs['form'] = MySuperuserForm
    #     return super().get_form(request, obj, **kwargs)

    # 自定义显示表单的Choice字段
    # 下例中通过重写 formfield_for_dbfield 方法给superuser多了一个选择
    def formfield_for_dbfield(self, db_field, **kwargs):
        print(db_field,  kwargs)
        if db_field.name == "status":
            kwargs['choices'] = (
                ('accepted', 'Accepted'),
                ('denied', 'Denied'),
            )
            if self.request.user.is_superuser:
                kwargs['choices'] += (('ready', 'Ready for deployment'),)
        return super().formfield_for_dbfield(db_field, **kwargs)


    # model form 保存方法  (重写)
    # def save_models(self):
    #     if self.form_obj.is_valid():
    #         if not self.form_obj.cleaned_data['slug']:
    #             self.new_obj.slug = uuid4().hex[:10]
    #         super().save_models()

    # Django的admin默认会展示所有对象。
    # 通过重写get_queryset方法，我们可以控制所需要获取的对象。
    # 比如下例中，我们先对用户进行判定，如果用户是超级用户就展示所有文章，如果不是超级用户，我们仅展示用户自己所发表的文章
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)



@register(CnTag)
class TagAdmin:
    ...


# 分类
@register(Category)
class CategoryAdmin:
    list_display = ['id', 'name', 'parent_category', 'slug']
    prepopulated_fields = {'slug':('name',)}  # 自动生成slug, 根据name填充slug
    search_fields = ['name',]
    ordering = ['parent_category'] 
