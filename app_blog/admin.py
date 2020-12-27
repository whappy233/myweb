from django.contrib import admin
from .models import Post, Comment
from uuid import uuid4
# 在这里注册模型，并将其纳入Django管理站点中

# admin.StackedInline
# admin.TabularInline
# admin.ModelAdmin


# admin.site.register(Post, PostAdmin)  # 注册方式1
@admin.register(Post)  # 注册方式2（使用包装）
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'id','slug', 'author', 'created', 'publish', 'updated', 'status']  # 显示字段
    search_fields = ['title', 'body']  # 搜索字段
    list_filter = ['publish', 'created', 'updated', 'status']  # 过滤器
    prepopulated_fields = {'slug':('title',)}  # 自动生成slug, 根据title填充slug
    raw_id_fields = ['author',]  # 下拉框改为微件
    actions_on_top = True   # 执行动作的位置
    # actions_on_bottom = False
    ordering = ['author']  # 默认排序
    # fields = ['title', 'slug', 'author', 'body', 'publish', 'status']  # 编辑页面的显示顺序

    # fieldsets = [
    #     (None, {'fields': ['question_text']}),
    #     ('Date information', {'fields': ['pub_date']}),
    # ]


    def save_model(self, request, obj, form, change):
        if form.is_valid():
            if not form.cleaned_data['slug']:
                obj.slug = uuid4().hex[:10]
            super().save_model(request, obj, form, change)




# admin.site.register(Comment)  # 注册方式1
@admin.register(Comment)  # 注册方式2（使用包装）
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'post', 'body', 'created', 'updated', 'active']  # 显示字段
    search_fields = ['name', 'email', 'body']  # 搜索字段
    list_filter = ['created', 'updated', 'active']  # 过滤器
    # raw_id_fields = ['post',]  # 下拉框改为微件



