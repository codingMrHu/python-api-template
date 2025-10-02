# -*- coding:utf-8 -*-
# @Author: H
# @Date: 2025-10-02
# @Version: 1.0
# @License: H
# @Desc: 腾讯云COS对象存储服务

import base64
import hashlib
import os
import uuid
from datetime import datetime
from io import BytesIO
from typing import Optional, Tuple

from PIL import Image as PILImage
from qcloud_cos import CosConfig, CosS3Client

from app.settings import settings
from app.utils.logger import logger


class COSService:
    """腾讯云COS对象存储服务"""

    def __init__(self):
        # 从配置文件读取腾讯云COS配置
        self.secret_id = settings.cos.secret_id
        self.secret_key = settings.cos.secret_key
        self.region = settings.cos.region
        self.bucket = settings.cos.bucket
        self.domain = settings.cos.domain

        if not all([self.secret_id, self.secret_key, self.bucket]):
            logger.warning("腾讯云COS配置不完整，请检查配置文件")
            self.client = None
        else:
            # 初始化COS客户端
            config = CosConfig(Region=self.region, SecretId=self.secret_id, SecretKey=self.secret_key, Scheme="https")
            self.client = CosS3Client(config)

    def _generate_cos_key(self, file_name: str, prefix: str = "images") -> str:
        """
        生成COS存储key
        :param file_name: 原始文件名
        :param prefix: 存储路径前缀
        :return: COS存储key
        """
        # 获取文件扩展名
        ext = os.path.splitext(file_name)[1] or ".jpg"
        # 生成唯一文件名: prefix/YYYYMM/uuid.ext
        date_path = datetime.now().strftime("%Y%m")
        unique_name = f"{uuid.uuid4().hex}{ext}"
        return f"{prefix}/{date_path}/{unique_name}"

    def _get_image_info(self, image_data: bytes) -> Tuple[Optional[int], Optional[int]]:
        """
        获取图片宽高信息
        :param image_data: 图片二进制数据
        :return: (width, height)
        """
        try:
            image = PILImage.open(BytesIO(image_data))
            return image.width, image.height
        except Exception as e:
            logger.error(f"获取图片信息失败: {e}")
            return None, None

    def _calculate_md5(self, data: bytes) -> str:
        """
        计算数据的MD5值
        :param data: 二进制数据
        :return: MD5字符串
        """
        return hashlib.md5(data).hexdigest()

    def upload_base64_image(self, base64_data: str, file_name: str, prefix: str = "images") -> dict:
        """
        上传base64编码的图片到腾讯云COS
        :param base64_data: base64编码的图片数据
        :param file_name: 原始文件名
        :param prefix: 存储路径前缀
        :return: 上传结果字典
        """
        if not self.client:
            raise ValueError("腾讯云COS客户端未初始化，请检查配置")

        try:
            # 解码base64数据
            # 如果包含data:image/jpeg;base64,前缀，先去除
            if "," in base64_data:
                base64_data = base64_data.split(",")[1]

            image_data = base64.b64decode(base64_data)

            # 获取图片信息
            width, height = self._get_image_info(image_data)
            md5_value = self._calculate_md5(image_data)

            # 生成COS存储key
            cos_key = self._generate_cos_key(file_name, prefix)

            # 上传到COS
            response = self.client.put_object(
                Bucket=self.bucket, Body=image_data, Key=cos_key, ContentType=self._get_content_type(file_name)
            )

            # 生成访问URL
            if self.domain:
                cos_url = f"https://{self.domain}/{cos_key}"
            else:
                cos_url = f"https://{self.bucket}.cos.{self.region}.myqcloud.com/{cos_key}"

            logger.info(f"图片上传成功: {cos_key}, ETag: {response.get('ETag')}")

            return {
                "cos_key": cos_key,
                "cos_url": cos_url,
                "bucket": self.bucket,
                "file_size": len(image_data),
                "width": width,
                "height": height,
                "md5": md5_value,
                "etag": response.get("ETag", "").strip('"'),
            }

        except Exception as e:
            logger.error(f"上传图片到COS失败: {e}")
            raise ValueError(f"上传图片失败: {str(e)}")

    def delete_image(self, cos_key: str) -> bool:
        """
        从COS删除图片
        :param cos_key: COS存储key
        :return: 是否成功
        """
        if not self.client:
            raise ValueError("腾讯云COS客户端未初始化，请检查配置")

        try:
            self.client.delete_object(Bucket=self.bucket, Key=cos_key)
            logger.info(f"图片删除成功: {cos_key}")
            return True
        except Exception as e:
            logger.error(f"删除COS图片失败: {e}")
            return False

    def _get_content_type(self, file_name: str) -> str:
        """
        根据文件名获取Content-Type
        :param file_name: 文件名
        :return: Content-Type
        """
        ext = os.path.splitext(file_name)[1].lower()
        content_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".bmp": "image/bmp",
            ".webp": "image/webp",
            ".svg": "image/svg+xml",
        }
        return content_types.get(ext, "image/jpeg")


# 创建全局COS服务实例
cos_service = COSService()
