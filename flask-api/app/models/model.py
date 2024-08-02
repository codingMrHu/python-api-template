# -*- coding:utf-8 -*-
# Author: 
# Date: 2023-06-16 14:34:25
# Version: 
# License: 
# Desc: 
import hmac
import hashlib
import base64
from datetime import datetime
from sqlalchemy.dialects.mysql import LONGTEXT,BOOLEAN,TEXT,DECIMAL, TINYINT
from configs.config import db
from app.models.base import BaseTimeModel

class User(BaseTimeModel):
    __abstract__ = False

    # 用户表
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    username = db.Column(db.String(100), comment='用户名称')
    phone = db.Column(db.String(100), comment='用户账号')
    password = db.Column(db.String(100), comment='用户密码')
    is_stop  = db.Column(TINYINT, server_default='0', comment='是否被封号')
    __table_args__ = ({'comment': '用户表'})

    @classmethod
    def encrypt_password(cls, password: str, salt: str) -> str:
        """加密

        Args:
            password (Union[str, bytes]): 密码明文
            salt (Union[str, bytes]): 盐值

        Returns:
            str: 加密后的 Base64 编码字符串
        """
        if isinstance(password, str):
            password = bytes(password, encoding='utf-8')
        if isinstance(salt, str):
            salt = bytes(salt, encoding='utf-8')

        hashing = hmac.new(password, salt, hashlib.sha256)
        return base64.b64encode(hashing.digest()).decode('utf-8')
