
# -*- coding:utf-8 -*-
# @Author: H
# @Date: 2024-07-18 14:12:10
# @Version: 1.0
# @License: H
# @Desc: 

class APIException(Exception):
    def __init__(self, message, err_code):
        super().__init__(message)
        self.err_code = err_code



class UnAuthorizedError(APIException):
    def __init__(self, message="暂无操作权限", err_code=403):
        super().__init__(message, err_code)

class InvalidArgument(APIException):
    """
    参数验证失败, 表单等用户传递的数据验证失败
    """
    def __init__(self, message="参数错误", err_code=422):
        super().__init__(message, err_code)