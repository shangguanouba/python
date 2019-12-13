# 定义索引类
from haystack import indexes
# 导入模型类
from goods.models import GoodsSKU


# 建立索引
class GoodsSKUIndex(indexes.SearchIndex, indexes.Indexable):
    # 索引字段
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        # 返回模型类
        return GoodsSKU

    # 建立索引数据
    def index_queryset(self, using=None):
        return self.get_model().objects.all()
