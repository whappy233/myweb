# 假设你有一个字典列表，你想根据某个或某几个字典字段来排序这个列表。
# 这时你需要使用 operator 模块的 itemgetter 函数，可以非常容易的排序这样的数据结构。 
# 假设你从数据库中检索出来网站会员信息列表，并且以下列的数据结构返回：

rows = [
    {'fname': 'Brian', 'lname': 'Jones', 'uid': 1003},
    {'fname': 'David', 'lname': 'Beazley', 'uid': 1002},
    {'fname': 'John', 'lname': 'Cleese', 'uid': 1001},
    {'fname': 'Big', 'lname': 'Jones', 'uid': 1004}]
# 根据任意的字典字段来排序输入结果行是很容易实现的，代码示例：

from operator import itemgetter

rows_by_fname = sorted(rows, key=itemgetter('fname'))

print(rows_by_fname)
# 代码的输出如下。注意该方法返回的直接排过序的完整字典，而不是排过序的键名列表。

[{'fname': 'Big', 'uid': 1004, 'lname': 'Jones'},

{'fname': 'Brian', 'uid': 1003, 'lname': 'Jones'},

{'fname': 'David', 'uid': 1002, 'lname': 'Beazley'},

{'fname': 'John', 'uid': 1001, 'lname': 'Cleese'}]
# itemgetter() 函数也支持多个 keys，比如下面的代码

rows_by_lfname = sorted(rows, key=itemgetter('lname','fname'))

print(rows_by_lfname)
# 输出如下:

[{'fname': 'David', 'uid': 1002, 'lname': 'Beazley'},

{'fname': 'John', 'uid': 1001, 'lname': 'Cleese'},

{'fname': 'Big', 'uid': 1004, 'lname': 'Jones'},

{'fname': 'Brian', 'uid': 1003, 'lname': 'Jones'}]