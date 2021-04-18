# django.contrib.humanize模块自带一组模板过滤器， 
# 可将数字或者日期转化为人类友好可读的格式，更人性化。
# 比如模板过滤器 naturaltime 可以将 2019-06-24 10:33:24 显示为 1 day ago。

# 使用该组模板过滤器时，你需要在 INSTALLED_APPS 加入 django.contrib.humanize 模块，并在模板里载入，如下所示。

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',  #
]


# 模板里先载入再使用。
# {% load humanize %} 

# {{ notification.date|naturaltime }}


# 其它过滤器作用如下:
# 过滤器             作用            举例
# apnumber        英文数字         1 => one
# intcomma        三位逗号数字      4500000 => 4,500,000
# intword         文本数字         4500000 => 4.5 million
# naturalday      友好的日期       2018-10-24 => yesterday
# naturaltime     友好的时间       2018-10-25 12:00:01 => a minute ago.
# ordinal         序数字符串       3 => 3rd