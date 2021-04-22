from flask import Flask
from flask_restful import Api
from flask_jwt_extended import *
from json import loads
import views

app = Flask(__name__)
# jwt_config = {}
# with open('../config/jwt_config.txt', 'r') as file:
#     jwt_config = loads(file.read())

#app.config.update(jwt_config)
app.config.update(Debug=True)
#jwt = JWTManager(app)
api = Api(app)
# api.add_resource(views.Test, '/test')

recommand = '/recommand'
api.add_resource(views.Recommand, recommand )


app.run(host='0.0.0.0', port=5000, debug=True)