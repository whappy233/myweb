
from django.shortcuts import HttpResponse
import time
from django.utils.deprecation import MiddlewareMixin


class SetRemoteAddrFromForwardedFor(MiddlewareMixin):
    """
    如果部署了代理，使用此中间件获取远程客户端IP。
    在settings中注册该中间件。
    """

    def process_request(self, request):
        try:
            real_ip = request.META['HTTP_X_FORWARDED_FOR']  # 关键一行
        except KeyError:
            ...
        else:
            real_ip = real_ip.split(',')[0]
            request.META['REMOTE_ADDR'] = real_ip


# x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')  # 获取真实ip
# if x_forwarded_for:
#     ip = x_forwarded_for.split(',')[0]  # 所以这里是真实的ip
# else:
#     ip = request.META.get('REMOTE_ADDR')  # 这里获得代理ip


# 访问IP池
visit_ip_pool = {}

class RequestBlockingMiddleware(MiddlewareMixin):
    '''IP访问频率控制'''

    def process_request(self, request):
        # 获取访问者IP
        ip = request.META.get("REMOTE_ADDR")
        # 获取访问当前时间
        visit_time = time.time()
        # 判断如果访问IP不在池中,就将访问的ip时间插入到对应ip的key值列表,如{"127.0.0.1":[时间1]}
        if ip not in visit_ip_pool:
            visit_ip_pool[ip] = [visit_time]
            return None
        # 然后在从池中取出时间列表
        history_time = visit_ip_pool.get(ip)
        # 循环判断当前ip的时间列表，有值，并且当前时间减去列表的最后一个时间大于60s，把这种数据pop掉，这样列表中只有60s以内的访问时间，
        while history_time and visit_time-history_time[-1] > 60:
            history_time.pop()
        # 如果访问次数小于50次就将访问的ip时间插入到对应ip的key值列表的第一位置,如{"127.0.0.1":[时间2,时间1]}
        print(history_time)
        if len(history_time) < 50:
            history_time.insert(0, visit_time)
            return None
        else:
            # 如果大于50次就禁止访问
            return HttpResponse(f"访问过于频繁, 还需等待{60-(visit_time-history_time[-1])}秒才能继续访问")
