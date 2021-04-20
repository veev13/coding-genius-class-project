from flask import Flask
from flask_restful import Api
from flask_jwt_extended import *
from json import loads
import views
import pymysql

app = Flask(__name__)
jwt_config = {}
db_config = None
with open('./config/jwt_config.txt', 'r') as file:
    jwt_config = loads(file.read())


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