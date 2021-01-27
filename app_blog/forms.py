# 表单
from django import forms
from .models import Article


# 邮件分享表单
class EmailArticleForm(forms.Form):
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


# 创建搜索表单
class SearchForm(forms.Form):
    q = forms.CharField(max_length=100 ,required=False)
