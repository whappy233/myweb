# 表单

from django import forms
from .models import Comment, Post
from ckeditor_uploader.widgets import CKEditorUploadingWidget  # 富文本编辑器表单组件



class PostForm(forms.ModelForm):
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




# 邮件分享表单
class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25, required=False, label='邮件主题')  # required 非必填项  <input type="text" name="name" maxlength="25" id="id_name">
    email = forms.EmailField(label='寄件人', required=False)   # <input type="email" name="email" id="id_email">
    to = forms.EmailField(label='收件人')   # <input type="email" name="to" required="" id="id_to">
    comments = forms.CharField(widget=forms.Textarea, label='邮件正文')   # <textarea name="comments" cols="40" rows="10" required="" id="id_comments"></textarea>

    # 自定义校验规则 必须以clean开头下划线连接字段名
    def clean_comments(self):
        comments = self.cleaned_data['comments']
        if len(comments) < 10:
            raise forms.ValidationError('不足20字')
        return comments


# 评论表单
# 从模型中创建表单(ModelForm)
# 当从模型中创建表单时，仅需指定使用哪一个模型创建 Meta 类中的表单
# 该方式以动态方法构建表单
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')  # 通知表单只创建哪些字段
        # exclude = (,) # 不创建的字段
        # widgets = {
        #     'name': forms.TextInput(attrs={'disabled': 'disabled'}),
        # }


# 创建搜索表单
class SearchForm(forms.Form):
    query = forms.CharField(max_length=100)
