from json import dumps, loads
from flask import Response, jsonify, request, wrappers
from flask_restful import Resource, Api
from flask_jwt_extended import *
import mariadb
from datetime import datetime, timedelta
import time
from recommand import get_min, get_max


db_config=loads(requests.get('http://http://3.237.78.43:30500/v1/kv/db_config?raw').text)

conn = mariadb.connect(**db_config)
cursor = conn.cursor()

#추천 종목 API
class Recommand(Resource):
    def get(self):
        

        max = """
        SELECT stock_id FROM Recommands WHERE similarity=(SELECT MAX(similarity) FROM Recommands ORDER BY updated_time DESC LIMIT 10)
        """
        min = """
        SELECT stock_id FROM Recommands WHERE similarity=(SELECT MIN(similarity) FROM Recommands ORDER BY updated_time DESC LIMIT 10)
        """

        cursor.execute(max)
        diff = cursor.fetchone()[0]
        cursor.execute(min)
        sim = cursor.fetchone()[0]
        json_data={"max":diff,"min":sim}
        return Response(dumps(json_data), status=200, mimetype='application/json')


