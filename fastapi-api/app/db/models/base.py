# -*- coding:utf-8 -*-
# @Author: H
# @Date: 2024-07-17 15:09:16
# @Version: 1.0
# @License: H
# @Desc:
import re
from datetime import datetime
from uuid import UUID
from typing import Optional

import orjson
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime, text
from app.api.errcode.base import InvalidArgument


def orjson_dumps(v, *, default=None, sort_keys=False, indent_2=True):
    option = orjson.OPT_SORT_KEYS if sort_keys else None
    if indent_2:
        # orjson.dumps returns bytes, to match standard json.dumps we need to decode
        # option
        # To modify how data is serialized, specify option. Each option is an integer constant in orjson.
        # To specify multiple options, mask them together, e.g., option=orjson.OPT_STRICT_INTEGER | orjson.OPT_NAIVE_UTC
        if option is None:
            option = orjson.OPT_INDENT_2
        else:
            option |= orjson.OPT_INDENT_2
    if default is None:
        return orjson.dumps(v, option=option).decode()
    return orjson.dumps(v, default=default, option=option).decode()


class SQLModelSerializableTime(SQLModel):
    create_time: Optional[datetime] = Field(
        default=None,
        sa_column_kwargs={
            "nullable": False,
            "server_default": text("CURRENT_TIMESTAMP"),
        },
    )
    update_time: Optional[datetime] = Field(
        default=None,
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
            "onupdate": text("CURRENT_TIMESTAMP"),
        },
    )


class SQLModelSerializable(SQLModel):
    class Config:
        orm_mode = True
        json_loads = orjson.loads
        json_dumps = orjson_dumps

    def to_dict(self):
        result = self.model_dump()
        for column in result:
            value = getattr(self, column)
            if isinstance(value, datetime):
                # 将datetime对象转换为字符串
                value = value.isoformat()
            elif isinstance(value, UUID):
                # 将UUID对象转换为字符串
                value = value.hex
            result[column] = value
        return result


def valid_char(_str: str, name: str = '', min_len: int = 0, max_len: int = 0, limit_len: int = 0):
    if min_len and len(_str) < min_len:
        raise InvalidArgument.http_exception(f'{name}应大于{min_len}位')
    if max_len and len(_str) > max_len:
        raise InvalidArgument.http_exception(f'{name}应小于{max_len + 1}位')
    if limit_len and len(_str) != limit_len:
        raise InvalidArgument.http_exception(f'{name}应为{limit_len}位')
    return _str


def match_char(_str: str, name: str):
    if not re.match(r'^[\u4e00-\u9fa5a-zA-Z\d]+$', _str):
        raise InvalidArgument.http_exception(f'{name}仅支持汉字、字母、数字。')
    return _str


def valid_name(name):
    return valid_char(name, name='姓名', min_len=1, max_len=35)


def valid_password(password: str):
    if not re.match(r'^(?=.*\d)(?=.*[A-Z])(?=.*[a-z])[\da-zA-Z\.\@\$\!\%\*#_~\?\&\^]{8,20}$', password):
        raise InvalidArgument.http_exception(
            '密码长度为8-20位，必须包含大小写字母和数字，可包含.@$!%*#_~?&^，请重新设置密码')
    return password


def valid_phone(phone: str):
    valid_char(phone, name='手机号', limit_len=11)
    if not re.match(r'^1[3-9]\d{9}$', phone):
        raise InvalidArgument.http_exception('手机号不正确')
    return phone


def valid_date(date: str):
    valid_char(date, name='日期', limit_len=10)
    try:
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        raise InvalidArgument.http_exception('日期格式不正确')
    return date


def valid_datetime(date_time: str):
    valid_char(date_time, name='日期', limit_len=19)
    try:
        datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        raise InvalidArgument.http_exception('日期格式不正确')
    return date_time


def valid_email(email: str):
    valid_char(email, name='邮箱', max_len=50)
    if not re.match(r'^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$', email):
        raise InvalidArgument.http_exception('邮箱格式不正确')
    return email
