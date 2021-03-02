session 会话


request.session.get(key, default=None)

request.session.pop(key, default=__not_given)

self.request.session[key] = value

del request.session['member_id']

request.session.clear()

request.session.flush()  # 删除当前会话和会话cookie

request.session.set_expiry(value)
为会话设置过期时间。你可以传递很多不同值：
value                   result
300                     使得会话在300s后过期
0                       则当浏览器关闭后过期
None                    会话会恢复为全局会话过期策略
datetime|timedelta 对象  会话将在指定的 date/time 过期。
注意，如果你正在使用 PickleSerializer ，那么 datetime 和 timedelta 的值只能序列化。



python manage.py clearsessions
可以以定时任务的形式运行，也可以直接清理过期会话