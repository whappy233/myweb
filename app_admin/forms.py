from django import forms
from app_blog.models import Post, Comment, Category
from ckeditor_uploader.widgets import CKEditorUploadingWidget  # 富文本编辑器表单组件



class ArticleCreateForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ['author', 'views', 'slug', 'publish', 'is_delete', 'users_like']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'body': CKEditorUploadingWidget(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'tags': forms.TextInput(attrs={'class': 'form-control'}),
        }

