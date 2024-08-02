# -*- coding:utf-8 -*-
# @Author: H
# @Date: 2023-10-09 16:46:19
# @Version: 1.0
# @License: H
# @Desc: 

#coding:utf-8
import os
from app.server.user import delete_user_record
from apscheduler.schedulers.background import BackgroundScheduler


# 增加判断避免debug下运行2个进程 导致在第一次运行时定时任务运行2次
print('init scheduler-----11', os.environ.get("WERKZEUG_RUN_MAIN"))
if os.environ.get("WERKZEUG_RUN_MAIN") is None:
    print('init scheduler-----22')
    scheduler = BackgroundScheduler()
    # 定时每天 23:59:59秒执行任务
    # scheduler.add_job(insert_stat,'cron',day_of_week ='0-6',hour = '*/1',minute = 1,second = 30)

    # 每天运行

    scheduler.add_job(delete_user_record,'cron',day_of_week ='0-6',hour = 0,minute = 0,second = 0)
    scheduler.start()