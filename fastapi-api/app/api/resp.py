# -*- coding:utf-8 -*-
# @Author: H
# @Date: 2024-07-12 17:20:41
# @Version: 1.0
# @License: H
# @Desc: 
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from pydantic import BaseModel

# 创建泛型变量
DataT = TypeVar('DataT')

# 继承自GenericModel 泛型响应模型会将 response_model类型转化返回
class UnifiedResponseModel(BaseModel, Generic[DataT]):
    """统一响应模型"""
    status_code: int
    status_message: str
    # 定义Dict[str, Union[List[DataT], Any]] 用于支持嵌套分页信息
    data: Optional[Union[DataT, Dict[str, Union[List[DataT], Any]], Any]] = None  


def resp_200(data: Union[list, dict, str, Any] = None,
             message: str = 'SUCCESS',
             page: Optional[Dict[str, Any]] = None) -> UnifiedResponseModel:
    """成功的代码"""
    if page:
        data = {"data": data, "page": page}  # 嵌套分页信息到data字段
    return UnifiedResponseModel(status_code=200, status_message=message, data=data)


def resp_500(code: int = 500,
             data: Union[list, dict, str, Any] = None,
             message: str = 'BAD REQUEST',
             page: Optional[Dict[str, Any]] = None) -> UnifiedResponseModel:
    """错误的逻辑回复"""
    if page:
        data = {"data": data, "page": page}  # 嵌套分页信息到data字段
    return UnifiedResponseModel(status_code=code, status_message=message, data=data)
