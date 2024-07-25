# -*- coding:utf-8 -*-
# @Author: H
# @Date: 2024-07-17 11:30:08
# @Version: 1.0
# @License: H
# @Desc: 


from app.api.resp import resp_200
from app.db.base import session_getter
from app.utils.logger import logger
from fastapi import APIRouter, HTTPException
from sqlmodel import select

# build router
router = APIRouter(prefix='/base', tags=['base'])