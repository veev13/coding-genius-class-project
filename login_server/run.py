from flask import Flask
from flask_restful import Api
from flask_jwt_extended import *
from json import loads
import views

app = Flask(__name__)

jwt_config = {}
with open('../config/jwt_config.txt', 'r') as file:
    jwt_config = loads(file.read())

print(jwt_config)
app.config.update(jwt_config)
# app.config.update(Debug=True)
jwt = JWTManager(app)
api = Api(app)

login = '/login'
api.add_resource(views.Login, login)
signup = '/signup'
api.add_resource(views.SignUp, signup)

app.run(host='0.0.0.0', port=5000, debug=True)