# -*- coding:utf-8 -*-
# @Author: H
# @Date: 2024-07-30 14:45:54
# @Version: 1.0
# @License: H
# @Desc: 
from configs.config import app, db

from app import api_base
from app.utils.utils import CustomJSONEncoder, success_json
from app import scheduler

app.json_encoder = CustomJSONEncoder
# db.create_all()


@app.route("/", methods=['POST', 'GET'])
def hello():
    return success_json("Hello World!")


if __name__ == '__main__':
    app.run('0.0.0.0', 5050, debug=False)
