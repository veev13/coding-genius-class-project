from json import dumps, loads
from flask import Response, jsonify, request, wrappers
from flask_restful import Resource, Api
from flask_jwt_extended import *
import mariadb
from datetime import datetime, timedelta
import time
import consul

c = consul.Consul(host='54.152.246.15', port=8500)
index = None


index, data = c.kv.get('recommand_db_config', index=index)
recommand_db_config = loads(data['Value'])


conn = mariadb.connect(**recommand_db_config)
cursor = conn.cursor()

# 추천 종목 API


class Recommand(Resource):
    def get(self):

        max = """
        SELECT stock_id FROM Recommands WHERE similarity=(SELECT MAX(similarity) FROM Recommands ORDER BY recommand_time DESC LIMIT 5)
        """
        min = """
        SELECT stock_id FROM Recommands WHERE similarity=(SELECT MIN(similarity) FROM Recommands ORDER BY recommand_time DESC LIMIT 5)
        """

        cursor.execute(max)
        diff = cursor.fetchone()[0]
        cursor.execute(min)
        sim = cursor.fetchone()[0]
        stock_code=["000660","005380","005490","005930","035720"]
        json_data = {"max": stock_code[diff-1], "min": stock_code[sim-1]}
        return Response(dumps(json_data), status=200, mimetype='application/json')
