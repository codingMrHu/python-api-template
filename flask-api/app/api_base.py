# -*- coding:utf-8 -*-
# @Author: H
# @Date: 2024-07-30 14:57:41
# @Version: 1.0
# @License: H
# @Desc: 

from configs.config import app
from app.api.user import user_bp
from app.utils.middlewares import handle_exception

# 注册蓝图
app.register_blueprint(user_bp, url_prefix='/api/user')


# 注册全局错误处理器
app.register_error_handler(Exception, handle_exception)
