# -*- coding:utf-8 -*-
# @Author: H
# @Date: 2024-07-18 14:15:25
# @Version: 1.0
# @License: H
# @Desc: 
import string
import random
import hashlib
from fastapi import Request, WebSocket


def get_request_ip(request: Request | WebSocket) -> str:
    """ 获取客户端真实IP """
    x_forwarded_for = request.headers.get('X-Forwarded-For')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.client.host


def md5_hash(original_string: str):
    md5 = hashlib.md5()
    md5.update(original_string.encode('utf-8'))
    return md5.hexdigest()

def random_str(length: int, only_digits=False, digits=False, upper=False, hexdigits=False):
    """ 生成随机字符串 """

    if only_digits:
        rand_str = string.digits
        return ''.join(random.choices(rand_str[1:], k=1)) + ''.join(random.choices(rand_str, k=length - 1))
    rand_str = string.ascii_lowercase[:6 if hexdigits else 26]
    if digits:
        rand_str += string.digits
    if upper:
        rand_str += string.ascii_uppercase[:6 if hexdigits else 26]
    return ''.join(random.choices(rand_str, k=length))

if __name__ == '__main__':
    print(random_str(10, only_digits=True))