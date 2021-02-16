from .models import Comments
from django import forms


# 评论表单
class CommentForm(forms.ModelForm):
    email = forms.EmailField(label='电子邮箱', required=True)
    name = forms.CharField(label='姓名', widget=forms.TextInput(attrs={
                                                'value': "",
                                                'size': "30",
                                                'maxlength': "245",
                                                'aria-required': 'true'}))
    class Meta:
        model = Comments
        fields = ['body', 'parent_comment']
        widgets = {
            'body': forms.Textarea(attrs={'placeholder':'支持MarkDown'}),
            'parent_comment': forms.HiddenInput()
        }