from views import app
from flask_jwt_extended import *
from json import loads
jwt_config = {}
with open('../config/jwt_config.txt', 'r') as file:
    jwt_config = loads(file.read())

app.config.update(jwt_config)
jwt = JWTManager(app)

app.run(host='0.0.0.0', port=8000)