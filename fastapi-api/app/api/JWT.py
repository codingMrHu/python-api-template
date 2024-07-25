# -*- coding:utf-8 -*-
# @Author: H
# @Date: 2024-07-17 10:05:28
# @Version: 1.0
# @License: H
# @Desc: 

from typing import List
from pydantic import BaseSettings
from app.settings import settings

# 配置JWT token的有效期
ACCESS_TOKEN_EXPIRE_TIME = settings.jwt_expires


class Settings(BaseSettings):
    authjwt_secret_key: str = settings.jwt_secret
    # Configure application to store and get JWT from cookies
    authjwt_token_location: List[str] = ['cookies', 'headers']
    # Disable CSRF Protection for this example. default is True
    authjwt_cookie_csrf_protect: bool = False


