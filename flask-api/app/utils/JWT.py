# -*- coding:utf-8 -*-
# @Author: H
# @Date: 2024-07-30 15:17:11
# @Version: 1.0
# @License: H
# @Desc: 

from flask import request, g
from authlib.jose import jwt, JoseError
from datetime import datetime, timedelta
from functools import wraps

from configs.config import SECRET_KEY
from app.utils.utils import error_json
from app.utils.error import InvalidArgument, UnAuthorizedError
from app import dao
from app.models.model import User

def generate_auth_token(uid, expiration = 60*60*24*7):
    """生成用于邮箱验证的JWT（json web token）"""
    # 签名算法
    header = {'alg': 'HS256'}
    # 用于签名的密钥
    # 待签名的数据负载
    expiration_date = datetime.utcnow() + timedelta(seconds=expiration)
    data = {'id': uid,'exp':expiration_date}
    return jwt.encode(header=header, payload=data, key=SECRET_KEY)

def get_user_by_token():
    token = request.headers.get('token')
    try:
        data = jwt.decode(token, SECRET_KEY)
        user_id = data['id']
        user = dao.select_one(User, User.id == user_id)
        if user.is_stop:
            raise UnAuthorizedError(u"系统检测到您的操作存在异常，因此进行冻结。如需解冻请留言进行申诉。")
    except Exception as e:
        raise UnAuthorizedError(u"由于长时间未登录，为保证帐号安全，请重新登录！")
    # 将请求的用户id 放到request中 后续使用
    return user

    
# 用户登陆认证
def verify_auth_token(func):
    @wraps(func)  # 设置函数的元信息
    def inner(*args, **kwargs):
        user = get_user_by_token()
        g.user = user
        return func(*args, **kwargs)

    return inner