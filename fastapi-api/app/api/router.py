# -*- coding:utf-8 -*-
# @Author: H
# @Date: 2024-07-12 17:11:44
# @Version: 1.0
# @License: H
# @Desc:

# Router for base api
from fastapi import APIRouter

from app.api.routers import img_router, user_router

router = APIRouter(
    prefix="/api",
)
router.include_router(user_router, tags=["user"])
router.include_router(img_router, tags=["img"])
