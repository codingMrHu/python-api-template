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

class CRUD(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    def create(self, session: Session, obj_in: T) -> T:
        session.add(obj_in)
        session.commit()
        session.refresh(obj_in)
        return obj_in

    def read(self, session: Session, *whereclause) -> Optional[T]:
        query: Select = select(self.model)
        query = query.where(*whereclause)
        
        return session.exec(query).first()
    
    def read_all(self, session: Session, *whereclause) -> List[T]:
        query: Select = select(self.model)
        
        query = query.where(*whereclause)

        return session.exec(query).all()

    def update(self, session: Session, obj_in: T) -> T:
        session.add(obj_in)
        session.commit()
        session.refresh(obj_in)
        return obj_in

    def delete(self, session: Session,  *whereclause) -> int:
        query: Select = select(self.model)
        
        query = self.model.__table__.delete()
        query = query.where(*whereclause)
        result = session.exec(query)
        session.commit()
        return result.rowcount
        return 0

    def paginate(
        self,
        session: Session,
        page: int = 1,
        page_size: int = PAGE_SIZE,
        *whereclause
    ) -> Tuple[List[T], int, int, int]:
        """分页查询"""
        offset = (page - 1) * page_size
        limit = page_size

        query = select(self.model)
        query = query.where(*whereclause)

        total = session.exec(select(func.count()).select_from(query.subquery())).one()
        items = session.exec(query.offset(offset).limit(limit)).all()
        
        # aginated_items, total, current_page, total_pages 
        return items, {"page_num":page,"page_size":page_size,"total_size":total}
    

# 增删查改  
def insert(model: Type[T], obj: T) -> T:
    with session_getter () as session:
        return CRUD(model).create(session, obj_in= obj)

def update(model: Type[T], obj: T) -> T:
    with session_getter () as session:
        return CRUD(model).update(session, obj_in= obj)

def delete(model: Type[T], id: [str, int], *whereclause) -> int:
    with session_getter () as session:
        return CRUD(model).delete(session, id= id, filters= filters)

def select_one(model: Type[T], *whereclause) -> T:
    with session_getter () as session:
        return CRUD(model).read(session, *whereclause)
    

def select_all(model: Type[T], *whereclause) -> List[T]:
    with session_getter () as session:
        return CRUD(model).read_all(session, *whereclause)

def select_page(model: Type[T],  page: int=1, page_size: int=PAGE_SIZE, *whereclause) -> Dict:
    with session_getter () as session:
        return CRUD(model).paginate(session, page, page_size, *whereclause)

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
    
def select_page_sql(sql: str,count_sql: str = None, page: int = 1, page_size: int = PAGE_SIZE) -> Dict:
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