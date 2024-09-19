# -*- coding:utf-8 -*-
# @Author: H
# @Date: 2024-07-22 21:17:21
# @Version: 1.0
# @License: H
# @Desc: 
import traceback
from typing import Type, TypeVar, Generic, List, Optional, Tuple, Any, Dict
from sqlmodel import SQLModel, Session, select
from sqlalchemy.sql import Select
from sqlalchemy.sql.functions import func
from sqlalchemy import text

from app.db.base import session_getter
from app.utils.logger import logger
from app.constants import PAGE_SIZE

T = TypeVar("T", bound=SQLModel)

# 增删查改  
def insert(obj: T) -> T:
    with session_getter () as session:
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

def update(model: Type[T], obj: T) -> T:
    with session_getter () as session:
        db_obj = session.get(model, obj.id)
        if not db_obj:
            return None
        for key, value in obj.model_dump().items():
            setattr(db_obj, key, value)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

def delete(model: Type[T],  *whereclause) -> int:
    with session_getter () as session:
        query: Select = select(model)
        query = model.__table__.delete()
        query = query.where(*whereclause)
        result = session.exec(query)
        session.commit()
        return result.rowcount

def exeute(query: Select) -> Any:
    with session_getter () as session:
        return session.exec(query).all()

def select_one(model: Type[T], *whereclause) -> T:
    with session_getter () as session:
        query: Select = select(model)
        query = query.where(*whereclause)
        return session.exec(query).first()
    
def select_all(model: Type[T], *whereclause, order_by: Optional[List[Any]] = None) -> List[T]:
    with session_getter () as session:
        query: Select = select(model)
        query = query.where(*whereclause)
        if order_by:
            query = query.order_by(*order_by)
        return session.exec(query).all()

def select_page(model: Type[T], page: int = 1, page_size: int = PAGE_SIZE, *whereclause, order_by: Optional[List[Any]] = None) -> Tuple:
    with session_getter() as session:
        """分页查询"""
        offset = (page - 1) * page_size
        limit = page_size

        query = select(model)
        query = query.where(*whereclause)
        
        if order_by:
            query = query.order_by(*order_by)

        total = session.exec(select(func.count()).select_from(query.subquery())).one()
        data = session.exec(query.offset(offset).limit(limit)).all()
        
        # paginated_data, total, current_page, total_pages 
        return data, {"page_num": page, "page_size": page_size, "total_size": total}


#--------------------------SQL CRUD
## input: string sql
## output : dictionary
def select_sql(sql: str) -> List[T]:
    logger.info(sql)
    with session_getter () as session:
        rows = session.execute(text(sql)).fetchall()
        return rows

def execute_sql(sql: str) -> int:
    logger.info(sql)
    with session_getter () as session:
        result = session.execute(text(sql))
        session.commit()
        return result.rowcount
    
def select_page_sql(sql: str,count_sql: str = None, page: int = 1, page_size: int = PAGE_SIZE) -> Tuple:
    offset = (page-1) * page_size
    sql = " %s limit %d,%d" % (sql, offset, PAGE_SIZE)
    data = select_sql(text(sql))

    if not count_sql:
        count_sql = "select count(1) as count "+sql[sql.find('from'):sql.find("limit")]
    data_count = select_sql(text(count_sql))
    size = 0
    if data_count:
        data_count = data_count[0]["count"]
    if data:
        size = len(data)
    return  data, {"page_num":page,"page_size":size,"total_size":data_count}