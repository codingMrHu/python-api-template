# -*- coding:utf-8 -*-
# @Author: H
# @Date: 2023-06-25 17:52:48
# @Version: 1.0
# @License: H
# @Desc: 

import os
import flask
import flask_cors
import flask_sqlalchemy
from urllib import parse

ENV = os.getenv('ENV', 'local')
print('env-------',ENV)
DIR_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_RESOURCE = os.path.join(DIR_BASE, 'resource')

app = flask.Flask(__name__)
flask_cors.CORS(app)

mysql_url = f'mysql+pymysql://root:root1234@localhost:3306/test?charset=utf8mb4'


PAGE_SIZE = 20

AVATAR_DIR='./images/avatar/'
AVATAR_URL='http://47.104.57.114/test/avatar/'
wechat_notify_url = 'https://www.weixin.qq.com/wxpay/pay.php'
signup_invite_path = ''
signup_invite_url = ''
invite_to_page = 'pages/grouper/grouper'

ERROR_CODE_MAP = {400:'参数错误',-1:'分组服务异常，请重试'}

SECRET_KEY = 'composer'
                 

vip_pay_desc = [
    {'user_level':'普通会员', 
     'permission':'1.提供国家版分组器的查询服务\n\
        2.提供国家版分组器的支付标准服务',
    'price':'-',
    'remark':'不登录无法使用任何服务。点击任意处，都跳转登录页面。'},
    {'user_level':'VIP会员', 
     'permission':'提供所有分组器的查询服务（无限次）、收藏记录',
    'price':'月卡30、季卡90、年卡228（6.3折）',
    'remark':'月卡计算方式：9.12～10.12\n季卡计算方式：9.12～12.12\n年卡计算方式：23.9.12～24.9.12'},
    ]

region_hospital_level = {'cn':{'hospital_level':['1','2', '3'], 'hospital_grade':[]}}

try:
    if ENV == 'prod':
        from configs.config_prod import *
    elif ENV == 'test':
        from configs.config_test import *
except Exception as ex:
    print('get env config failed, Exception: ' + str(ex))


# Flask-SQLAlchemy config  http://www.pythondoc.com/flask-sqlalchemy/config.html
app.config['SQLALCHEMY_ECHO'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = mysql_url
# 解决中文问题
app.config['JSON_AS_ASCII'] = False
# 解决jsonify对返回的json数据进行排序
app.config['JSON_SORT_KEYS'] = False
db = flask_sqlalchemy.SQLAlchemy(app)
