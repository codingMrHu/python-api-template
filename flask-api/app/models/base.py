# -*- coding:utf-8 -*-
# @Author: H
# @Date: 2024-07-30 15:21:45
# @Version: 1.0
# @License: H
# @Desc: 

from configs.config import db

class BaseTimeModel(db.Model):
    __abstract__ = True
    ctime = db.Column(db.DateTime, server_default=db.text('CURRENT_TIMESTAMP'))
    utime = db.Column(db.DateTime, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}