# -*- coding:utf-8 -*-
# @Author: H
# @Date: 2024-07-30 15:04:28
# @Version: 1.0
# @License: H
# @Desc: 

from flask import Blueprint, jsonify, request
from app.utils.utils import success_json, error_json
from app import dao
from app.models.model import User
from app.utils import JWT
from configs.config import SECRET_KEY

# 创建一个蓝图对象
user_bp = Blueprint('user', __name__)

@user_bp.route('/<int:id>', methods=['GET'])
@JWT.verify_auth_token
def get_user(id):
    # 示例实现：从数据库获取用户
    data =  dao.select(User, User.id==id)
    data = [x.to_dict() for x in data]
    return success_json(data)

@user_bp.route('/', methods=['POST'])
def create_user():
    # 示例实现：创建新用户
    data = request.get_json()
    if dao.select_one(User, User.username==data['username']):
        return error_json('用户名已存在')
    if dao.select_one(User, User.phone==data['phone']):
        return error_json('用户手机号已存在')
    
    data['password'] = User.encrypt_password(data['password'], SECRET_KEY)
    res = dao.insert(User, data)
    return success_json(res)


@user_bp.route('/login', methods=['POST'])
def login():
    # 示例实现：创建新用户
    data = request.get_json()
    
    user = dao.select_one(User, User.phone==data['phone'])
    if not user or user.password!= User.encrypt_password(data['password'], SECRET_KEY):
        return error_json('用户名或密码错误')
    
    token = JWT.generate_auth_token(user.id)
    res = user.to_dict()
    res['token'] = token
    return success_json(res)
