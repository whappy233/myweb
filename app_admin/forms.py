from django import forms
from app_blog.models import Article
from ckeditor_uploader.widgets import CKEditorUploadingWidget  # 富文本编辑器 ckeditor 表单小部件
from mdeditor.widgets import MDEditorWidget  # 富文本编辑器 mdeditor 表单小部件
from taggit.forms import TagWidget  # 第三方标签小部件

# from mdeditor.fields import MDTextFormField  # 富文本编辑器 mdeditor 表单字段
# class MDEditorForm(forms.Form):
#     name = forms.CharField()
#     content = MDTextFormField()
# ModelForm 可自动将model 对应的字段转为 form字段， 可正常使用：
# class MDEditorModleForm(forms.ModelForm):
#     class Meta:
#         model = Article
#         fields = '__all__'

class ArticleCreateForm(forms.ModelForm):
    class Meta:
        model = Article
        exclude = ['author', 'views', 'slug', 'publish', 'is_delete', 'users_like']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            # 'body': CKEditorUploadingWidget(attrs={'class': 'form-control'}),
            'body': MDEditorWidget(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'tags': TagWidget(attrs={'class': 'form-control'}),
        }

