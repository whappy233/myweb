from .models import Comments
from django import forms


# 评论表单
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ['body', 'parent_comment']
        widgets = {
            'parent_comment': forms.HiddenInput
        }