# 1. 安装前的准备
# 如果你需要上传和显示图片，请先确保已安装了pillow图片库，并按文一设置STATIC和MEDIA文件夹。


# 2. 安装ckeditor
# 使用pip install django-ckeditor安装ckeditor, 在项目文件夹下(而不是app文件夹下)新建static文件夹, 使用python manage.py collectstatic下载ckeditor所需的js和css文件。


# 3. 设置settings.py
# 在 INSTALLED_APPS 中添加:
INSTALLED_APPS = [
    # ...
    'ckeditor', # 第三方富文本编辑器 pip install django-ckeditor==6.0.0
    'ckeditor_uploader', # 第三方富文本编辑器_文件组件
]

# 在settings.py里添加CKEDITOR的设置，如下所示。我们指定了图片上传文件夹"blog_uploads", 最后图片会上传到/media/blog_uploads/文件夹里。由于我们还选择了RESTRICT_BY_USER和RESTRICT_BY_DATE, 最后图片实际上传地址如下所示:
# /media/blog_uploads/Chris/2018/09/09/img_4961.JPG
# CKEDITOR_CONFIGS可以设置显示在工具栏toolbar的按钮。

from ckeditor_uploader.widgets import CKEditorUploadingWidget
from .models import Article
from django import forms
from ckeditor_uploader.fields import RichTextUploadingField
CKEDITOR_UPLOAD_PATH = 'blog_uploads/'
CKEDITOR_JQUERY_URL = 'https://apps.bdimg.com/libs/jquery/2.1.4/jquery.min.js'
CKEDITOR_IMAGE_BACKEND = 'pillow'
CKEDITOR_ALLOW_NONIMAGE_FILES = False
CKEDITOR_BROWSE_SHOW_DIRS = True
CKEDITOR_RESTRICT_BY_USER = True
CKEDITOR_RESTRICT_BY_DATE = True


CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': (['Source', '-',  'Preview', '-', ],
                    ['Cut', 'Copy', 'Paste', 'PasteText',
                        'PasteFromWord', '-', 'Print', 'SpellChecker', ],
                    ['Undo', 'Redo', '-', 'Find', 'Replace', '-', 'SelectAll', 'RemoveFormat', '-',
                     "CodeSnippet", 'Subscript', 'Superscript'],
                    ['NumberedList', 'BulletedList', '-', 'Blockquote'],
                    ['Link', 'Unlink', ],
                    ['Image', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar', ],
                    ['Format', 'Font', 'FontSize', 'TextColor', 'BGColor', ],
                    ['Bold', 'Italic', 'Underline', 'Strike', ],
                    ['JustifyLeft', 'JustifyCenter',
                        'JustifyRight', 'JustifyBlock'],
                    ),
        'extraPlugins': 'codesnippet',
        'width': 'auto',
    }
}


# 4. 模型中使用ckeditor
# 我们只需将body的TextField改成RichTextUploadingField。如果你不需要上传图片，可以直接使用RichTextField。
class Article(models.Model):
    """文章模型"""
    STATUS_CHOICES = (
        ('d', '草稿'),
        ('p', '发表'),
    )

    title = models.CharField('标题', max_length=200, unique=True)
    slug = models.SlugField('slug', max_length=60, blank=True)
    body = RichTextUploadingField('正文')


# 5. 表单中使用ckeditor
# 因为我们使用到了表单，所以表单的输入widget还需要改为CKEditorUploadingWidget.
class ArticleForm(forms.ModelForm):

    class Meta:
        model = Article
        exclude = ['author', 'views', 'slug', 'pub_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'body': CKEditorUploadingWidget(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'tags': forms.CheckboxSelectMultiple(attrs={'class': 'multi-checkbox'}),
        }


# 6. 模板中使用{{form.media}}调入ckeditor静态文件
# 模板中如果不使用{{form.media}}调入ckeditor静态文件(js, css和图片), 那么前端你将看不到漂亮的用户界面。
'''
<form method = "POST" class = "form-horizontal" role = "form" action = "" >
  { % csrf_token % }
    {{form.media}}
 ......
'''


# 7. 修改staff_member_required装饰器变为login_required。
# 这一点是在admin内和admin外使用ckeditor最的不同。如果需要使用文件上传，ckeditor默认只有员工(staff member)才有这个权限。
# 如果你需要admin外的用户也能上传图片或文件，你需要将staff_member_required装饰器改为login_required。
# 你需要按 site-packages => ckeditor_uploader => urls.py 的源码，把staff_member_required装饰器改为login_required。


# 8. 显示代码
# 只需要在 CKEDITOR_CONFIGS 中加入 codesnipppet 的 plugin 即可。

'extraPlugins': 'codesnippet',
# 同时找到 site-packages => ckeditor => static => ckeditor => ckeditor =>config.js 把codesnippet注册一下。
# CKEDITOR.editorConfig = function( config ) {
#    // Define changes to default configuration here. For example:
#    // config.language = 'fr';
#    // config.uiColor = '#AADC6E';
#    config.extraPlugins: "codesnippet";

# 9. 在根URL 中添加:
    re_path(r'^ckeditor/', include('ckeditor_uploader.urls')),