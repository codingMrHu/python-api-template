# -*- coding:utf-8 -*-
# @Author: H
# @Date: 2024-07-18 14:37:22
# @Version: 1.0
# @License: H
# @Desc: 

from typing import Any, List
from uuid import UUID

from loguru import logger

from app.db.models.audit_log import AuditLog, SystemId, EventType, ObjectType, AuditLogDao
from app.api.resp import resp_200
from app.db.models.user import User
from app.db.dao import insert


class AuditLogService:

    @classmethod
    def _system_log(cls, user: User, ip_address: str, event_type: EventType,
                    object_type: ObjectType, object_id: str, object_name: str, note: str = ''):

        audit_log = AuditLog(
            operator_id=user.id,
            operator_name=user.user_name,
            system_id=SystemId.SYSTEM.value,
            event_type=event_type.value,
            object_type=object_type.value,
            object_id=object_id,
            object_name=object_name,
            ip_address=ip_address,
            note=note,
        )
        insert(audit_log)
        

    @classmethod
    def insert_user(cls, user: User, ip_address: str, note: str = '新建用户'):
        """
        修改用户的
        """
        logger.info(f"act=update_system_user user={user.user_name} ip={ip_address} user_id={user.id} note={note}")
        cls._system_log(user, ip_address, EventType.USER_CREATE, 
                        ObjectType.USER_CONF, str(user.id), user.user_name, note)
        
    @classmethod
    def update_user(cls, user: User, ip_address: str, note: str):
        """
        修改用户的
        """
        logger.info(f"act=update_system_user user={user.user_name} ip={ip_address} user_id={user.id} note={note}")
        cls._system_log(user, ip_address, EventType.UPDATE_USER, 
                        ObjectType.USER_CONF, str(user.id), user.user_name, note)


    @classmethod
    def user_login(cls, user: User, ip_address: str):
        logger.info(f"act=user_login user={user.user_name} ip={ip_address} user_id={user.id}")
        # 获取用户所属的分组
        cls._system_log(user, ip_address, EventType.USER_LOGIN, ObjectType.NONE, '', '')
