# -*- coding:utf-8 -*-
# @Author: H
# @Date: 2024-07-18 15:38:02
# @Version: 1.0
# @License: H
# @Desc: 
from fastapi import FastAPI, HTTPException
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional, Generic, TypeVar
from pydantic import BaseModel
from pydantic.generics import GenericModel

# 定义泛型类型 T
T = TypeVar("T")

# 定义泛型响应模型
class APIResponse(GenericModel, Generic[T]):
    status_code: int
    status_msg: str
    data: Optional[T]

def rsp_200(data: T = None):
    return APIResponse(status_code=200, status_msg="success", data=data)

# 定义 SQLModel 模型
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str

# 定义 Pydantic 模型
class UserCreate(BaseModel):
    name: str
    email: str

class UserRead(BaseModel):
    name: str

    class Config:
        orm_mode = True

# 创建数据库引擎
engine = create_engine("sqlite:///database.db")
SQLModel.metadata.create_all(engine)

# 创建 FastAPI 应用
app = FastAPI()

# 定义路由
@app.post("/users/", response_model=APIResponse[UserRead])
async def create_user(user: UserCreate):
    with Session(engine) as session:
        db_user = User.from_orm(user)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return APIResponse(status_code=201, status_msg="User created", data=db_user)

@app.get("/users/{user_id}", response_model=APIResponse[UserRead])
async def read_user(user_id: int):
    with Session(engine) as session:
        user = session.get(User, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return rsp_200(data=user)

# 运行服务器
# uvicorn main:app --reload





if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=7866, workers=1)
