# -*- coding:utf-8 -*-
# @Author: H
# @Date: 2024-07-12 17:20:41
# @Version: 1.0
# @License: H
# @Desc:
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

from pydantic import BaseModel

# 创建泛型变量
DataT = TypeVar("DataT")


class PaginationInfo(BaseModel):
    """分页信息模型"""

    page_num: int
    page_size: int
    total_size: int

    @property
    def total_pages(self) -> int:
        """计算总页数"""
        if self.page_size == 0:
            return 0
        return (self.total_size + self.page_size - 1) // self.page_size

    @property
    def has_next(self) -> bool:
        """是否有下一页"""
        return self.page_num < self.total_pages

    @property
    def has_prev(self) -> bool:
        """是否有上一页"""
        return self.page_num > 1


class PaginatedData(BaseModel, Generic[DataT]):
    """分页数据模型"""

    data: List[DataT]
    pagination: PaginationInfo


class UnifiedResponseModel(BaseModel, Generic[DataT]):
    """统一响应模型"""

    code: int
    message: str  # 修复拼写错误
    data: Optional[DataT] = None
    detail: Optional[str] = None


class ResponseBuilder:
    """响应构建器，用于解耦响应逻辑"""

    @staticmethod
    def success(data: Any = None, message: str = "SUCCESS", code: int = 200) -> UnifiedResponseModel:
        """构建成功响应"""
        return UnifiedResponseModel(code=code, message=message, data=data)

    @staticmethod
    def success_with_pagination(
        data: List[Any], pagination: PaginationInfo, message: str = "SUCCESS", code: int = 200
    ) -> UnifiedResponseModel[PaginatedData]:
        """构建带分页的成功响应"""
        paginated_data = PaginatedData(data=data, pagination=pagination)
        return UnifiedResponseModel(code=code, message=message, data=paginated_data)

    @staticmethod
    def error(
        code: int = 500, message: str = "BAD REQUEST", data: Any = None, detail: Optional[str] = None
    ) -> UnifiedResponseModel:
        """构建错误响应"""
        return UnifiedResponseModel(code=code, message=message, data=data, detail=detail)


# 便捷的响应函数（推荐使用）
def success_response(data: Any = None, message: str = "SUCCESS") -> UnifiedResponseModel:
    """成功响应"""
    return ResponseBuilder.success(data, message)


def error_response(code: int = 500, message: str = "BAD REQUEST", detail: Optional[str] = None) -> UnifiedResponseModel:
    """错误响应"""
    return ResponseBuilder.error(code, message, detail=detail)


def paginated_response(
    data: List[Any], page_num: int, page_size: int, total_size: int, message: str = "SUCCESS"
) -> UnifiedResponseModel[PaginatedData]:
    """分页响应"""
    pagination = PaginationInfo(page_num=page_num, page_size=page_size, total_size=total_size)
    return ResponseBuilder.success_with_pagination(data, pagination, message)
