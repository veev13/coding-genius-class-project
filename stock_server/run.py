from flask import Flask
from flask_restful import Api
from flask_jwt_extended import *
from json import loads
import views
import pymysql
import requests

app = Flask(__name__)
db_config=loads(requests.get('http://http://3.237.78.43:30500/v1/kv/db_config?raw').text)
jwt_config = loads(requests.get('http://3.237.78.43:30500/v1/kv/jwt_config?raw').text)

app.config.update(jwt_config)
app.config.update(Debug=True)
jwt = JWTManager(app)
api = Api(app)
api.add_resource(views.Test, '/test')

stocks = '/stocks'
api.add_resource(views.StockSell, stocks + '/sell')
api.add_resource(views.StockBuy, stocks + '/buy')
api.add_resource(views.StockAlarms, stocks + '/alarms') # 알람설정 API
api.add_resource(views.StockList, stocks) # 주식 목록 API

users = '/users'
api.add_resource(views.StockStatus, users + '/stocks')
api.add_resource(views.UserPoint, users + '/point')

app.run(host='0.0.0.0', port=5000, debug=True)