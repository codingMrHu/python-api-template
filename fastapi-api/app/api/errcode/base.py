# -*- coding:utf-8 -*-
# @Author: H
# @Date: 2024-07-18 14:12:10
# @Version: 1.0
# @License: H
# @Desc:

from fastapi.exceptions import HTTPException

from app.api.resp import error_response


class BaseErrorCode(Exception):
    """
    基础错误类，继承自Exception，可以直接被raise
    错误码前三位代表具体功能模块，后两位表示模块内部具体的报错。例如10001
    """

    code: int
    message: str

    def __init__(self, message: str = None, detail: any = None):
        self.message = message or self.message
        self.detail = detail
        super().__init__(self.message)

    def to_http_exception(self) -> HTTPException:
        """转换为HTTPException"""
        return HTTPException(status_code=self.code, detail=self.message)

    def return_resp(self) -> error_response:
        """返回统一响应格式"""
        return error_response(code=self.code, message=self.message, detail=self.detail)


class ApiError(BaseErrorCode):
    code: int = 500
    message: str = "服务异常"


class UnAuthorizedError(BaseErrorCode):
    code: int = 403
    message: str = "暂无操作权限"


class InvalidArgument(BaseErrorCode):
    """
    参数验证失败, 表单等用户传递的数据验证失败
    """

    code: int = 422
    message: str = "参数错误"
