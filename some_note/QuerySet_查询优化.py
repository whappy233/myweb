# Django的QuerySet自带缓存(Cache)
# 例2比例3要好，因为在你打印文章标题后，Django不仅执行了查询，还把查询到的post_list放在了缓存里。
# 这个post_list是可以复用的。例3就不行了。
# Example 2: Good
post_list = Post.objects.filter(title__contains="django")
for post in post_list:
    print(post.title)

# Example 3: Bad
for post in Post.objects.filter(title__contains="django"):
    print(post.title)




# 用if也会导致queryset的执行
# 有时我们只希望了解查询的结果是否存在，而不需要使用整个数据集
# 这时你可以用 exists() 方法。
# 与if判断不同，exists 只会检查查询结果是否存在，返回True或False，而不会缓存post_list(见例5）
# 判断查询结果是否存在到底用if还是exists取决于你是否希望缓存查询数据集复用，如果是用if，反之用exists。
# Example 5: Good
post_list = Post.objects.filter(title__contains="django")
if post_list.exists():
    print("Records found.")
else:
    print("No records")




# 统计查询结果数量优选count方法
# len()与count()均能统计查询结果的数量。
# 一般来说count更快，因为它是从数据库层面直接获取查询结果的数量，而不是返回整个数据集，而len会导致queryset的执行，需要将整个queryset载入内存后才能统计其长度。
# 但事情也没有绝对，如果数据集queryset已经在缓存里了，使用len更快，因为它不需要跟数据库再次打交道
# 下面三个例子中，只有例7最差，尽量不要用。
# Example 6: Good
count = Post.objects.filter(title__contains="django").count()  # 没有缓存时

# Example 7:Bad
count = Post.objects.filter(title__contains="django").len()

# Example 8: Good
post_list = Post.objects.filter(title__contains="django")
if post_list:  # 在这里缓存了查询结果
    print("{} records found.".format(post_list.len()))




# 当queryset非常大时，数据请按需去取
# 当查询到的queryset的非常大时，会大量占用内存(缓存)。
# 我们可以使用values和value_list方法按需提取数据。
# 比如我们只需要打印文章标题，这时我们完全没有必要把每篇文章对象的全部信息都提取出来载入到内存中。我们可以做如下改进（例9）
# values和values_list返回的是字典形式字符串数据，而不是对象集合。如果不理解请不要乱用
# Example 9: Good
post_list = Post.objects.filter(title__contains="django").values('title')
if post_list:
    print(post.title)

post_list = Post.objects.filter(title__contains="django").values_list('id', 'title')
if post_list:
    print(post.title)




# 更新数据库部分字段请用update方法
# 如果需要对数据库中的某条已有数据或某些字段进行更新，更好的方式是用update，而不是save方法。
# 我们现在可以对比下面两个案例。
# 例10中需要把整个Post对象的数据(标题，正文.....)先提取出来，缓存到内存中，变更信息后再写入数据库。
# 而例11直接对标题做了更新，不需要把整个文章对象的数据载入内存，显然更高效。
# 尽管单篇文章占用内存不多，但是万一用户非常多呢，那么占用的内存加起来也是很恐怖的
# Example 10: Bad
post = Post.objects.get(id=10)
Post.title = "Django"
post.save()

# Example 11: Good
Post.objects.filter(id=10).update(title='Django')  # 返回已更新条目的数量




# 专业地使用explain方法
# Django 2.1中QuerySet新增了explain方法，可以统计一个查询所消耗的执行时间。这可以帮助程序员更好地优化查询结果
print(Blog.objects.filter(title='My Blog').explain(verbose=True))
# output
# Seq Scan on public.blog  (cost=0.00..35.50 rows=10 width=12) (actual time=0.004..0.004 rows=10 loops=1)
#   Output: id, title
#   Filter: (blog.title = 'My Blog'::bpchar)
# Planning time: 0.064 ms
# Execution time: 0.058 ms