# -*- coding:utf-8 -*-
# @Author: H
# @Date: 2025-10-02
# @Version: 1.0
# @License: H
# @Desc: 图片管理路由

from typing import Optional

from fastapi import APIRouter, Depends, Request

from app.api.errcode.base import ApiError
from app.api.resp import UnifiedResponseModel, error_response, success_response
from app.api.services.cos_service import cos_service
from app.api.services.user_service import get_login_user
from app.db import dao
from app.db.models.img import Image, ImageCreate, ImageQuery, ImageRead, ImageUpdate
from app.db.models.user import User
from app.utils.logger import logger

# 创建路由
router = APIRouter(prefix="/img", tags=["Image"])


@router.post("/upload", response_model=UnifiedResponseModel[ImageRead])
async def upload_image(*, request: Request, image_data: ImageCreate, login_user: User = Depends(get_login_user)):
    """
    上传图片到腾讯云COS并记录到数据库
    """
    try:
        # 上传到腾讯云COS
        upload_result = cos_service.upload_base64_image(
            base64_data=image_data.file_data, file_name=image_data.file_name
        )

        # 创建数据库记录
        db_image = Image(
            file_name=image_data.file_name,
            file_size=upload_result["file_size"],
            file_type=image_data.file_type,
            cos_url=upload_result["cos_url"],
            cos_key=upload_result["cos_key"],
            bucket=upload_result["bucket"],
            md5=upload_result["md5"],
            width=upload_result["width"],
            height=upload_result["height"],
            uploader_id=login_user.id,
            status=1,
            remark=image_data.remark,
        )

        # 保存到数据库
        dao.insert(db_image)

        logger.info(f"用户 {login_user.user_name} 上传图片成功: {db_image.file_name}")

        return success_response(db_image)

    except ValueError as e:
        raise ApiError(message=str(e))
    except Exception as e:
        logger.error(f"上传图片失败: {e}")
        raise ApiError(message="上传图片失败，请稍后重试")


@router.get("/list", response_model=UnifiedResponseModel)
async def list_images(
    *,
    file_name: Optional[str] = None,
    uploader_id: Optional[int] = None,
    status: Optional[int] = None,
    page_num: int = 1,
    page_size: int = 10,
    login_user: User = Depends(get_login_user),
):
    """
    获取图片列表（分页）
    """
    filters = []

    if file_name:
        filters.append(Image.file_name.like(f"%{file_name}%"))

    if uploader_id is not None:
        filters.append(Image.uploader_id == uploader_id)

    if status is not None:
        filters.append(Image.status == status)

    # 非管理员只能查看自己上传的图片
    if not login_user.is_admin:
        filters.append(Image.uploader_id == login_user.id)

    data, page = dao.select_page(Image, page_num, page_size, *filters, order_by=[Image.id.desc()])

    return success_response(data=data, page=page)


@router.get("/detail/{image_id}", response_model=UnifiedResponseModel[ImageRead])
async def get_image_detail(*, image_id: int, login_user: User = Depends(get_login_user)):
    """
    获取图片详情
    """
    db_image = dao.select_one(Image, Image.id == image_id)

    if not db_image:
        raise ApiError(message="图片不存在")

    # 非管理员只能查看自己上传的图片
    if not login_user.is_admin and db_image.uploader_id != login_user.id:
        raise ApiError(message="无权限查看此图片")

    return success_response(db_image)


@router.put("/update", response_model=UnifiedResponseModel[ImageRead])
async def update_image(*, image_update: ImageUpdate, login_user: User = Depends(get_login_user)):
    """
    更新图片信息（仅支持更新文件名、备注、状态）
    """
    db_image = dao.select_one(Image, Image.id == image_update.id)

    if not db_image:
        raise ApiError(message="图片不存在")

    # 非管理员只能更新自己上传的图片
    if not login_user.is_admin and db_image.uploader_id != login_user.id:
        raise ApiError(message="无权限修改此图片")

    # 更新字段
    if image_update.file_name:
        db_image.file_name = image_update.file_name

    if image_update.remark is not None:
        db_image.remark = image_update.remark

    if image_update.status is not None and login_user.is_admin:
        db_image.status = image_update.status

    dao.update(Image, db_image)

    logger.info(f"用户 {login_user.user_name} 更新图片信息: {db_image.id}")

    return success_response(db_image)


@router.delete("/delete/{image_id}", response_model=UnifiedResponseModel)
async def delete_image(*, image_id: int, permanent: bool = False, login_user: User = Depends(get_login_user)):
    """
    删除图片
    :param image_id: 图片ID
    :param permanent: 是否永久删除（同时删除COS文件），默认只标记删除
    """
    db_image = dao.select_one(Image, Image.id == image_id)

    if not db_image:
        raise ApiError(message="图片不存在")

    # 非管理员只能删除自己上传的图片
    if not login_user.is_admin and db_image.uploader_id != login_user.id:
        raise ApiError(message="无权限删除此图片")

    if permanent:
        # 永久删除：从COS删除文件并删除数据库记录
        try:
            cos_service.delete_image(db_image.cos_key)
        except Exception as e:
            logger.warning(f"删除COS文件失败: {e}")

        dao.delete(Image, Image.id == image_id)
        logger.info(f"用户 {login_user.user_name} 永久删除图片: {image_id}")
        return success_response(message="图片已永久删除")
    else:
        # 标记删除
        db_image.status = 0
        dao.update(Image, db_image)
        logger.info(f"用户 {login_user.user_name} 标记删除图片: {image_id}")
        return success_response(message="图片已删除")


@router.post("/batch_delete", response_model=UnifiedResponseModel)
async def batch_delete_images(
    *, image_ids: list[int], permanent: bool = False, login_user: User = Depends(get_login_user)
):
    """
    批量删除图片
    """
    if not image_ids:
        raise ApiError(message="请选择要删除的图片")

    success_count = 0
    fail_count = 0

    for image_id in image_ids:
        try:
            db_image = dao.select_one(Image, Image.id == image_id)

            if not db_image:
                fail_count += 1
                continue

            # 非管理员只能删除自己上传的图片
            if not login_user.is_admin and db_image.uploader_id != login_user.id:
                fail_count += 1
                continue

            if permanent:
                try:
                    cos_service.delete_image(db_image.cos_key)
                except Exception as e:
                    logger.warning(f"删除COS文件失败: {e}")

                dao.delete(Image, Image.id == image_id)
            else:
                db_image.status = 0
                dao.update(Image, db_image)

            success_count += 1

        except Exception as e:
            logger.error(f"删除图片 {image_id} 失败: {e}")
            fail_count += 1

    return success_response(message=f"成功删除 {success_count} 张图片，失败 {fail_count} 张")
