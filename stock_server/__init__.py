from flask import Flask
from flask_restful import Api
from flask_jwt_extended import *
import views

app = Flask(__name__)
app.config.update(
    Debug=True,
    JWT_SECRET_KEY="test",
    JWT_ACCESS_TOKEN_EXPIRES=1200,
)
jwt = JWTManager(app)
api = Api(app)
api.add_resource(views.Test, '/test')

stocks = '/stocks'
api.add_resource(views.StockSell, stocks + '/sell')
api.add_resource(views.StockBuy, stocks + '/buy')

users = '/users'
api.add_resource(views.StockStatus, users + '/stocks')
api.add_resource(views.UserPoint, users + '/point')
