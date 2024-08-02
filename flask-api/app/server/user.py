# -*- coding:utf-8 -*-
# @Author: H
# @Date: 2024-07-30 15:04:46
# @Version: 1.0
# @License: H
# @Desc: 

from datetime import datetime, timedelta
from app import dao
from app.utils.log_utils import logger

# 刷新用户权限及剩余查询次数信息
def delete_user_record():
    # 删除两个月前的请求记录---
    start = (datetime.now() - timedelta(days=30*2)).strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f'delete_user_record-------------{start}')
    dao.execute_sql(f"delete from user_record where ctime<'{start}' ")