from flask import Flask
from flask_restful import Api
from flask_jwt_extended import *
from json import loads
import views
import pymysql
import consul
import consul

app = Flask(__name__)

c = consul.Consul(host='54.152.246.15', port=30500)
index = None
index, data = c.kv.get('jwt_config', index=index)
jwt_config = loads(data['Value'])

app.config.update(jwt_config)
app.config.update(Debug=True)
jwt = JWTManager(app)
api = Api(app)
api.add_resource(views.Test, '/test')

stocks = '/stocks'
api.add_resource(views.StockSell, stocks + '/sell')
api.add_resource(views.StockBuy, stocks + '/buy')
api.add_resource(views.StockAlarms, stocks + '/alarms')  # 알람설정 API
api.add_resource(views.StockList, stocks)  # 주식 목록 API

users = '/users'
api.add_resource(views.StockStatus, users + '/stocks')
api.add_resource(views.UserPoint, users + '/point')

app.run(host='0.0.0.0', port=5000, debug=True)
