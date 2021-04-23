from flask import Flask
from flask_restful import Api
from flask_jwt_extended import *
from json import loads
import views
import requests

app = Flask(__name__)



jwt_config = loads(requests.get('http://3.237.78.43:30500/v1/kv/jwt_config?raw').text)


app.config.update(jwt_config)
jwt = JWTManager(app)


api = Api(app)

login = '/login'
api.add_resource(views.Login, login)
signup = '/signup'
api.add_resource(views.SignUp, signup)

app.run(host='0.0.0.0', port=5001, debug=True)
