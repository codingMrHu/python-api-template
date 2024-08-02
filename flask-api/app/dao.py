# -*- coding:utf-8 -*-
# @Author: H
# @Date: 2023-06-25 16:22:02
# @Version: 1.0
# @License: H
# @Desc: 

import math
from sqlalchemy.sql import text
import traceback
from configs.config import PAGE_SIZE, db, app
from app.utils.log_utils import logger

app.app_context().push()


# orm------------------
def select(model, query):
    return model.query.filter(query)


def select_one(model, query):
    return model.query.filter(query).first()


def insert(model, dict_data):
    try:
        record = model(**dict_data)
        db.session.add(record)
        db.session.commit()
        if hasattr(record, 'id'):
            return record.id
        return True
    except Exception as e:
        db.session.rollback()
        logger.error("Error: trace:%s", traceback.format_exc())
        logger.error("Error: unable to insert:%s" % str(dict_data))
        raise Exception(e)


def delete(model, id):
    result = model.query.filter_by(id=id).delete()
    db.session.commit()
    return result


# model为表
# id为主键
# dict_data为dict，key必须和表字段相同
def update(model, id, dict_data, pkey='id'):
    #remove default PK
    try:
        if pkey in dict_data:
            del dict_data[pkey]

        #select by id
        newRecord = model.query.get(id)

        #update
        for key, value in dict_data.items():
            setattr(newRecord, key, value)

        #model.query.filter_by(id=id).update(record) #这种update方式，返回结果是id。row的内容还是需要查询。
        db.session.commit()
        return newRecord
    except Exception as e:
        db.session.rollback()
        logger.error("Error: trace:%s", traceback.format_exc())
        logger.error("Error: unable to update:%s" % str(dict_data))
        raise Exception(e)


#--------------------------SQL CRUD
## input: string sql
## output : dictionary
def select_sql(sql):
    logger.info(sql)
    try:
        rows = db.session.execute(text(sql)).fetchall()
        db.session.commit()
        return [dict(row._mapping) for row in rows]
    except Exception:
        traceback.print_exc()
        logger.error("Error: unable to execute sql:%s" % sql)
    return None


def execute_sql(sql):
    logger.info(sql)
    try:
        res = db.session.execute(text(sql))
        db.session.commit()
        if sql.lower().strip().startswith('insert'):
            return res.lastrowid
        return res.rowcount
    except Exception:
        traceback.print_exc()
        logger.error("Error: unable to execute sql:%s" % sql)
    return None


def select_page_sql(sql, pagenum, PAGE_SIZE=PAGE_SIZE):
    offset = (pagenum - 1) * PAGE_SIZE
    sql = " %s limit %d,%d" % (sql, offset, PAGE_SIZE)
    data = select_sql(text(sql))

    countsql = "select count(1) as count " + sql[sql.find('from'):sql.find("limit")]
    data_count = select_sql(text(countsql))
    db.session.commit()
    size = 0
    if data_count:
        data_count = data_count[0]["count"]
    if data:
        size = len(data)
    res = {"data": data, "page": {"page_num": pagenum, "page_size": size, "total_size": data_count}}
    return res


if __name__ == '__main__':
    pass
