# -*- coding:utf-8 -*-
# @Author: H
# @Date: 2024-07-17 10:25:34
# @Version: 1.0
# @License: H
# @Desc: 
import os
from loguru import logger
from app.db.base import  db_service


def init_default_data():
    """初始化数据库"""
    try:
        # 初始化表
        db_service.create_db_and_tables()
        # with session_getter() as session:
        #     pass
            # TODO: 初始化数据
    except Exception as exc:
        # if the exception involves tables already existing
        # we can ignore it
        if 'already exists' not in str(exc):
            logger.error(f'Error creating DB and tables: {exc}')
            raise RuntimeError('Error creating DB and tables') from exc


def read_from_conf(file_path: str) -> str:
    if '/' not in file_path:
        # Get current path
        current_path = os.path.dirname(os.path.abspath(__file__))

        file_path = os.path.join(current_path, file_path)

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    return content
