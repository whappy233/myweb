



'''
shell 脚本: nginx_log.sh

    NGINX=/usr/local/nginx/  # 设置变量
    $NGINX/sbin/nginx -s stop  # 停止 Nginx
    mv $NGINX/logs/access.log ~/nginx_logs/  # 移动日志文件
    $NGINX/sbin/nginx  # 启动 Nginx，会自动生成日志文件
    workon django  # 进入 虚拟环境
    /root/project/xxxx.py  # 执行 Python 脚本

'''



'''
crontab 设置
    2 0 * * * /bin/sh /root/nginx_log.sh
每天的两点定时执行 shell 脚本
'''



# python 脚本: xxxx.py

import os
import sys
import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "path.settings")  # 如果不用 django 提供的 cache，可以直接导入 Redis 包
django.setup()


class Pv:
    def __init__(self):
        self.file = open('/root/nginx_logs/access.log', 'r')  # 日志路径

    def foo(self):
        import re
        res = re.finditer('(\\d+\\.\\d+\\.\\d+\\.\\d+).*?\\n', self.file.read())  # 正则切分
        for i in res:
            yield i.group(1)

    def result(self):
        lis = []
        for i in self.foo():
            if len(lis):     # lis 为空，会发生越界错误
                if i == lis[-1]:
                    continue
            lis.append(i)
        from django.core.cache import cache
        pv = cache.get('nginx_pv') or 1    # 如果不存在则为1，否则为None时，不同类型相加会报错
        cache.set('nginx_pv', lis.__len__() + pv)
        return lis.__len__()

    def __del__(self):
        self.file.close()   # 关闭文件

    def __str__(self):
        return str(self.result())

