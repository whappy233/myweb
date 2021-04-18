'''
========================================================================
aggregate()  --> {key: value}
'''

# aggregate的中文意思是聚合, 源于SQL的聚合函数。
# Django 的 aggregate() 方法作用是对一组值(比如queryset的某个字段)进行统计计算，并以字典(Dict)格式返回统计计算结果。
# django的aggregate方法支持的聚合操作有 AVG / COUNT / MAX / MIN /SUM 等

from django.db import models

class Hobby(models.Model):
    name = models.CharField(max_length=20)

class Student(models.Model):
    name = models.CharField(max_length=20)
    age = models.IntegerField()
    hobbies = models.ManyToManyField(Hobby)


from django.db.models import Avg, Count, Max, Min, Sum


# 计算学生平均年龄, 返回字典。age和avg间是双下划线哦
Student.objects.all().aggregate(Avg('age'))
{ 'age__avg': 12 }

# 学生平均年龄，返回字典。all()不是必须的
Student.objects.aggregate(Avg('age'))
{ 'age__avg': 12 }

# 计算学生总年龄, 返回字典。
Student.objects.aggregate(Sum('age'))
{ 'age__sum': 144 }

# 学生平均年龄, 设置字典的key
Student.objects.aggregate(average_age = Avg('age'))
{ 'average_age': 12 }

# 学生最大年龄，返回字典
Student.objects.aggregate(Max('age'))
{ 'age__max': 12 }

# 同时获取学生年龄均值, 最大值和最小值, 返回字典
Student.objects.aggregate(Avg('age'), Max('age'), Min('age'))
{ 'age__avg': 12, 'age__max': 18, 'age__min': 6, }

# 根据Hobby反查学生最大年龄。查询字段student和age间有双下划线哦。
Hobby.objects.aggregate(Max('student__age'))
{ 'student__age__max': 12 }


'''
========================================================================
annotate() 分组 --> queryset
'''
# 按学生分组，统计每个学生的爱好数量
Student.objects.annotate(Count('hobbies'))
# 返回的结果依然是Student查询集，只不过多了hobbies__count这个字段。
# 如果你不喜欢这个默认名字，你当然可以对这个字段进行自定义从而使它变得更直观。

# 按学生分组，统计每个学生爱好数量，并自定义字段名
Student.objects.annotate(hobby_count_by_student=Count('hobbies'))

# 按爱好分组，再统计每组学生数量。
Hobby.objects.annotate(Count('student'))

# 按爱好分组，再统计每组学生最大年龄。
Hobby.objects.annotate(Max('student__age'))


'annotate 方法与 Filter 方法联用'
# 有时我们需要先对数据集先筛选再分组，有时我们还需要先分组再对查询集进行筛选。
# 根据需求不同，我们可以合理地联用annotate方法和filter方法。
# 注意: annotate 和 filter 方法联用时使用顺序很重要。

# 先按爱好分组，再统计每组学生数量, 然后筛选出学生数量大于1的爱好。
Hobby.objects.annotate(student_num=Count('student')).filter(student_num__gt=1)

# 先按爱好分组，筛选出以'd'开头的爱好，再统计每组学生数量。
Hobby.objects.filter(name__startswith="d").annotate(student_num=Count('student'))


'annotate与order_by()联用'
# 我们同样可以使用order_by方法对annotate方法返回的数据集进行排序。

# 先按爱好分组，再统计每组学生数量, 然后按每组学生数量大小对爱好排序。
Hobby.objects.annotate(student_num=Count('student')).order_by('student_num')

# 统计最受学生欢迎的5个爱好。
Hobby.objects.annotate(student_num=Count('student')).order_by('-student_num')[:5]


'annotate与values()联用'
# 我们在前例中按学生对象进行分组，我们同样可以按学生姓名name来进行分组。
# 唯一区别是本例中，如果两个学生具有相同名字，那么他们的爱好数量将叠加。

# 按学生名字分组，统计每个学生的爱好数量
Student.objects.values('name').annotate(Count('hobbies'))

# 速查询数据表字段重复条目
Student.objects.values('first_name').annotate(name_count=Count('first_name')).filter(name_count__gt=1)

# 你还可以使用values方法从annotate返回的数据集里提取你所需要的字段，如下所示:
# 按学生名字分组，统计每个学生的爱好数量。
Student.objects.annotate(hobby_count=Count('hobbies')).values('name', 'hobby_count')