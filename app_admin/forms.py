from django import forms
from app_blog.models import Article, Comment, Category
from ckeditor_uploader.widgets import CKEditorUploadingWidget  # 富文本编辑器表单组件

from taggit.forms import TagWidget

class ArticleCreateForm(forms.ModelForm):
    class Meta:
        model = Article
        exclude = ['author', 'views', 'slug', 'publish', 'is_delete', 'users_like']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'body': CKEditorUploadingWidget(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'tags': TagWidget(attrs={'class': 'form-control'}),
        }

