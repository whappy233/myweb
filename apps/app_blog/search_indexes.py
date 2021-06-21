
# 想针对某个 app 例如 app_blog 做全文检索, 则必须在 app_blog 的目录下面建立 search_indexes.py 文件, 且文件名不能修改.


from haystack import indexes
from .models import Article

# 类名必须为需要检索的 Model_name+Index, 这里需要检索 Article, 所以创建 NoteIndex
class ArticleIndex(indexes.SearchIndex, indexes.Indexable):

    # 每个索引里面必须有且只能有一个字段为 document=True, 这代表haystack 和搜索引擎将使用此字段的内容作为索引进行检索(primary field).
    # 其他的字段只是附属的属性, 方便调用, 并不作为检索数据.
    # 如果使用一个字段设置了document=True, 则一般约定此字段名为text, 这是在SearchIndex类里面一贯的命名, 以防止后台混乱, 不建议改.
    text = indexes.CharField(document=True, use_template=True)  # 创建一个text字段

    # 创建一个 body 字段, model_attr='body' 代表对应数据模型 Article 中的 body 字段
    body = indexes.CharField(model_attr='body')
    title = indexes.CharField(model_attr='title')
    summary = indexes.CharField(model_attr='summary')

    # 重载get_model方法. 对哪张表进行查询. 必须要有！
    def get_model(self):
        return Article

    def index_queryset(self, using=None):  # 重载index_..函数
        """Used when the entire index for model is updated."""
        return self.get_model().published.all()
