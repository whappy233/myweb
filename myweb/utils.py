import base64
import copy
import hmac
import json
import time
from hashlib import md5

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.cache import cache
from loguru import logger


def get_md5(str):
    '''字符串转MD5'''
    m = md5(str.encode('utf-8'))
    return m.hexdigest()



class GenerateEncrypted:
    @staticmethod
    def encode(payload:dict, key:str=settings.SECRET_KEY, exp:int=3600)->str:
        npayload = copy.deepcopy(payload)
        npayload['exp'] = time.time() + exp
        npayload_json = json.dumps(npayload, separators=(',',':'))
        hc = hmac.new(key.encode(), npayload_json.encode(), digestmod='SHA256').hexdigest()
        sign = base64.urlsafe_b64encode((npayload_json+'|'+hc).encode()).decode()
        return sign

    @staticmethod
    def decode(sign:str, key:str=settings.SECRET_KEY):
        try:
            payload_json, hc = base64.urlsafe_b64decode(sign).decode().split('|')
            hc0 = hmac.new(key.encode(), payload_json.encode(), digestmod='SHA256').hexdigest()
            if hc0 == hc:
                payload = json.loads(payload_json)
                exp = payload.get('exp', 0)
                if time.time()>exp:
                    return False
                return payload
            else:
                return False
        except:
            return False


def cache_decorator(expiration=3 * 60):
    def wrapper(func):
        def news(*args, **kwargs):
            try:
                view = args[0]
                key = view.get_cache_key()
            except BaseException:
                key = None
            if not key:
                unique_str = repr((func, args, kwargs))

                m = md5(unique_str.encode('utf-8'))
                key = m.hexdigest()
            value = cache.get(key)
            if value is not None:
                # logger.info('cache_decorator get cache:%s key:%s' % (func.__name__, key))
                if str(value) == '__default_cache_value__':
                    return None
                else:
                    return value
            else:
                logger.info('cache_decorator set cache:%s key:%s' %(func.__name__, key))
                value = func(*args, **kwargs)
                if value is None:
                    cache.set(key, '__default_cache_value__', expiration)
                else:
                    cache.set(key, value, expiration)
                return value
        return news
    return wrapper


@cache_decorator()
def get_current_site():
    site = Site.objects.get_current()
    return site


def send_email(emailto, title, content):
    from DjangoBlog.blog_signals import send_email_signal
    send_email_signal.send(
        send_email.__class__,
        emailto=emailto,
        title=title,
        content=content)
