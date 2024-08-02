# -*- coding:utf-8 -*-
# @Author: H
# @Date: 2024-07-30 15:47:38
# @Version: 1.0
# @License: H
# @Desc: 
import traceback
from app.utils.utils import error_json
from app.utils.log_utils import logger
from app.utils.error import APIException, InvalidArgument

def handle_exception(e):
    if isinstance(e, APIException):
        logger.error(f'{e}')
        return error_json(str(e), e.err_code)
    
    # logger.error(f'服务异常:{traceback.format_exc()} {e}')
    return error_json(f'服务异常: {e}')

