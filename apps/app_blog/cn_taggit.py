# taggit 支持中文 slug

from taggit.models import Tag, TaggedItem
from django.utils.text import slugify
from django.urls import reverse


class CnTag(Tag):
    class Meta:
        proxy = True
        verbose_name = '标签'
        verbose_name_plural = verbose_name

    def get_absolute_url(self):
        return reverse('app_blog:article_list_by_tag', args=[self.slug])

    def slugify(self, tag, i=None):
        return slugify(tag, allow_unicode=True)[:128]



class CnTaggedItem(TaggedItem):
    '''taggit 支持中文 slug'''
    class Meta:
        proxy = True

    @classmethod
    def tag_model(cls):
        return CnTag