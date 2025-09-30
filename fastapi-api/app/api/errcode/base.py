# -*- coding:utf-8 -*-
# @Author: H
# @Date: 2024-07-18 14:12:10
# @Version: 1.0
# @License: H
# @Desc:

from app.api.resp import UnifiedResponseModel
from fastapi.exceptions import HTTPException


class BaseErrorCode:
    # 错误码前三位代表具体功能模块，后两位表示模块内部具体的报错。例如10001
    Code: int
    Msg: str

    @classmethod
    def return_resp(cls, msg: str = None, data: any = None) -> UnifiedResponseModel:
        return UnifiedResponseModel(status_code=cls.Code, status_message=msg or cls.Msg, data=data)

    @classmethod
    def http_exception(cls, msg: str = None) -> Exception:
        return HTTPException(status_code=cls.Code, detail=msg or cls.Msg)


class UnAuthorizedError(BaseErrorCode):
    Code: int = 403
    Msg: str = "暂无操作权限"


class InvalidArgument(BaseErrorCode):
    """
    参数验证失败, 表单等用户传递的数据验证失败
    """

    Code = 422
    Msg = "参数错误"
