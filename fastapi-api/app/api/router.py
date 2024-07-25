# -*- coding:utf-8 -*-
# @Author: H
# @Date: 2024-07-12 17:11:44
# @Version: 1.0
# @License: H
# @Desc: 

# Router for base api
from app.api.routers import *
from fastapi import APIRouter

router = APIRouter(prefix='/api', )
router.include_router(user_router, tags=['user'])
