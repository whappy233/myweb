'''使用F方法更新一个对象或多个对象字段'''

# 通常情况下我们在更新数据时需要先从数据库里将原数据取出后放在内存里，然后编辑某些字段或属性，最后提交更新数据库。
# 使用F方法则可以帮助我们避免将所有数据先载入内存，而是直接生成SQL语句更新数据库。


# 假如我们需要对所有产品的价格涨20%，我们通常做法如下。
# 当产品很少的时候，对网站性能没影响。
# 但如果产品数量非常多，把它们信息全部先载入内存会造成很大性能浪费。

products = Product.objects.all()
for product in products:
    product.price *= 1.2
    product.save()


# 使用F方法可以解决上述问题。我们直接可以更新数据库，而不必将所有产品载入内存。
from django.db.models import F
Product.objects.update(price=F('price') * 1.2)


# 我们也可以使用F方法更新单个对象的字段，如下所示：
product = Product.objects.get(pk=5009)
product.price = F('price') * 1.2
product.save()


# 但值得注意的是当你使用F方法对某个对象字段进行更新后，需要使用refresh_from_db()方法后才能获取最新的字段信息（非常重要！)。如下所示：
product.price = F('price') + 1
product.save()
print(product.price)            # <CombinedExpression: F(price) + Value(1)>
product.refresh_from_db()
print(product.price)            # Decimal('13.00')