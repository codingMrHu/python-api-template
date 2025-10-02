# -*- coding:utf-8 -*-
# @Author: H
# @Date: 2024-07-12 17:24:51
# @Version: 1.0
# @License: H
# @Desc:
import os
import traceback
import uuid
from contextlib import contextmanager

from sqlmodel import Session

from app.db.service import DatabaseService
from app.settings import settings
from app.utils.logger import logger

db_service: "DatabaseService" = DatabaseService(settings.database.url)


@contextmanager
def session_getter() -> Session:
    """轻量级session context"""
    try:
        session = Session(db_service.engine)
        yield session
    except Exception:
        logger.info(f"Session rollback because of exception:{traceback.format_exc()}")
        session.rollback()
        raise
    finally:
        session.close()


def read_from_conf(file_path: str) -> str:
    if "/" not in file_path:
        # Get current path
        current_path = os.path.dirname(os.path.abspath(__file__))

        file_path = os.path.join(current_path, file_path)

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    return content


def generate_uuid() -> str:
    """
    生成uuid的字符串
    """
    return uuid.uuid4().hex
