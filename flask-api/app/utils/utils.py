# -*- coding:utf-8 -*-
# @Author: H
# @Date: 2023-06-30 14:26:00
# @Version: 1.0
# @License: H
# @Desc: 
import json
import decimal
from flask import jsonify,make_response
from datetime import datetime,timedelta


def gen_indice_dict(lst: list):
    return {item: idx for idx, item in enumerate(lst)}

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(o, bytes):
            return o.decode()
        elif isinstance(o, decimal.Decimal):
            return float(o)
        # elif isinstance(o, np.floating):
        #     return float(o)
        return json.JSONEncoder.default(self, o)

def tojson(obj):
    rsp = make_response(json.dumps(obj,cls=CustomJSONEncoder).encode('utf-8'))
    rsp.mimetype = 'application/json'
    return rsp
    # return jsonify(obj)

def error_json(msg, err_code=500):
    obj = {}
    obj["success"] = False
    obj["message"] = msg
    obj["err_code"] = err_code
    rsp = tojson(obj)
    return rsp

def success_json(data):
    obj = {}
    obj["success"] = True
    obj["message"] = "success"
    obj["err_code"] = 200
    obj["data"] = data
    rsp = tojson(obj)
    return rsp


    