from flask import Flask
from flask_restful import Api
from flask_jwt_extended import *
import views

app = Flask(__name__)
app.config.update(jwt_config)
app.config.update(Debug=True)
jwt = JWTManager(app)
api = Api(app)
api.add_resource(views.Test, '/test')

stocks = '/stocks'
api.add_resource(views.StockSell, stocks + '/sell')
api.add_resource(views.StockBuy, stocks + '/buy')

users = '/users'
api.add_resource(views.StockStatus, users + '/stocks')
api.add_resource(views.UserPoint, users + '/point')

app.run(host='0.0.0.0', port=5000, debug=True)