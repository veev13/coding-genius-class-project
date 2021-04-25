from flask import Flask
from flask_restful import Api
from flask_jwt_extended import *
from json import loads
import views
import consul

app = Flask(__name__)

c = consul.Consul(host='54.152.246.15', port=8500)
index = None
index, data = c.kv.get('jwt_config', index=index)
jwt_config = loads(data['Value'])

app.config.update(jwt_config)
jwt = JWTManager(app)

api = Api(app)

login = '/login'
api.add_resource(views.Login, login)
signup = '/signup'
api.add_resource(views.SignUp, signup)

app.run(host='0.0.0.0', port=15001)
