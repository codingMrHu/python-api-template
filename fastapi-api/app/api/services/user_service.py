# -*- coding:utf-8 -*-
# @Author: H
# @Date: 2024-07-18 14:37:22
# @Version: 1.0
# @License: H
# @Desc:

import functools
import json
from typing import List

from fastapi import Depends, HTTPException
from fastapi_jwt_auth import AuthJWT

from app.api.errcode.base import UnAuthorizedError
from app.api.errcode.user import UserLoginOfflineError
from app.api.JWT import ACCESS_TOKEN_EXPIRE_TIME
from app.db.dao import select_one
from app.db.models.user import AdminRole, User


def gen_user_jwt(db_user: User):
    if 1 == db_user.delete:
        raise ApiError(message="该账号已被禁用，请联系管理员")
    # 生成JWT令牌
    payload = {"user_name": db_user.user_name, "user_id": db_user.id, "role": db_user.role}
    # Create the tokens and passing to set_access_cookies or set_refresh_cookies
    access_token = AuthJWT().create_access_token(subject=json.dumps(payload), expires_time=ACCESS_TOKEN_EXPIRE_TIME)

    refresh_token = AuthJWT().create_refresh_token(subject=db_user.user_name)

    # Set the JWT cookies in the response
    return access_token, refresh_token


async def get_login_user(authorize: AuthJWT = Depends()) -> User:
    """
    获取当前登录的用户
    """
    # 校验是否过期，过期则直接返回http 状态码的 401
    authorize.jwt_required()

    current_user = json.loads(authorize.get_jwt_subject())

    # 获取access_token
    user = select_one(User, User.id == current_user["user_id"])
    # 登录被挤下线了，http状态码是200, code是特殊code
    if user.current_token != authorize._token:
        raise UserLoginOfflineError()
    return user
