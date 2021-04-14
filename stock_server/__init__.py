from flask import Flask
from flask_restful import Api
import views
app = Flask(__name__)

api = Api(app)

stocks = '/stocks'
api.add_resource(views.StockSell, stocks+'/sell')
api.add_resource(views.StockBuy, stocks+'/buy')

users = '/users'
api.add_resource(views.StockStatus, users+'/stocks')
api.add_resource(views.UserPoint, users+'/point')