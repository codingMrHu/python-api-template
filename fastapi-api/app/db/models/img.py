# -*- coding:utf-8 -*-
# @Author: H
# @Date: 2025-10-02
# @Version: 1.0
# @License: H
# @Desc: 图片文件管理模型

from datetime import datetime
from typing import Optional

from pydantic import field_validator
from sqlalchemy import Column, Integer, String, Text
from sqlmodel import Field

from app.db.models.base import (
    SQLModelSerializable,
    SQLModelSerializableTime,
)


class ImageBase(SQLModelSerializable):
    """图片基础模型"""

    file_name: str = Field(index=True, description="原始文件名")
    file_size: int = Field(default=0, description="文件大小(字节)")
    file_type: str = Field(default="image/jpeg", description="文件类型")
    cos_url: str = Field(sa_column=Column(String(length=512)), description="腾讯云COS访问URL")
    cos_key: str = Field(sa_column=Column(String(length=512)), description="COS存储key")
    bucket: str = Field(default="", description="存储桶名称")
    md5: Optional[str] = Field(default=None, description="文件MD5值")
    width: Optional[int] = Field(default=None, description="图片宽度")
    height: Optional[int] = Field(default=None, description="图片高度")
    uploader_id: Optional[int] = Field(default=None, foreign_key="user.id", description="上传用户ID")
    status: int = Field(default=1, description="状态: 1-正常, 0-已删除")
    remark: Optional[str] = Field(default=None, sa_column=Column(Text), description="备注")


class Image(ImageBase, SQLModelSerializableTime, table=True):
    """图片数据库模型"""

    __tablename__ = "image"

    id: Optional[int] = Field(default=None, primary_key=True)

    @property
    def file_size_kb(self) -> float:
        """返回文件大小(KB)"""
        return round(self.file_size / 1024, 2)

    @property
    def file_size_mb(self) -> float:
        """返回文件大小(MB)"""
        return round(self.file_size / (1024 * 1024), 2)


class ImageCreate(SQLModelSerializable):
    """创建图片请求模型"""

    file_name: str = Field(description="原始文件名")
    file_data: str = Field(description="base64编码的图片数据")
    file_type: Optional[str] = Field(default="image/jpeg", description="文件类型")
    remark: Optional[str] = Field(default=None, description="备注")

    @field_validator("file_name")
    def validate_file_name(cls, v):
        if not v or len(v) > 255:
            raise ValueError("文件名不能为空且长度不能超过255")
        return v

    @field_validator("file_data")
    def validate_file_data(cls, v):
        if not v:
            raise ValueError("图片数据不能为空")
        # 检查是否是base64格式
        if "," in v:
            # 支持 data:image/jpeg;base64,xxx 格式
            v = v.split(",")[1]
        return v


class ImageUpdate(SQLModelSerializable):
    """更新图片请求模型"""

    id: int = Field(description="图片ID")
    file_name: Optional[str] = Field(default=None, description="原始文件名")
    remark: Optional[str] = Field(default=None, description="备注")
    status: Optional[int] = Field(default=None, description="状态")


class ImageRead(ImageBase):
    """图片响应模型"""

    id: int
    create_time: datetime
    update_time: datetime

    class Config:
        from_attributes = True


class ImageQuery(SQLModelSerializable):
    """图片查询模型"""

    file_name: Optional[str] = Field(default=None, description="文件名(模糊查询)")
    uploader_id: Optional[int] = Field(default=None, description="上传者ID")
    status: Optional[int] = Field(default=None, description="状态")
    page_num: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=10, ge=1, le=100, description="每页数量")
