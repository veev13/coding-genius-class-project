from flask import Flask
from flask_restful import Api
from flask_jwt_extended import *
from json import loads
import views

app = Flask(__name__)

app.config.update(Debug=True)

api = Api(app)


recommand = '/recommand'
api.add_resource(views.Recommand, recommand )


app.run(host='0.0.0.0', port=5000, debug=True)