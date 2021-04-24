from views import app
from flask_jwt_extended import *
from json import loads
import requests
jwt_config = loads(requests.get('http://3.237.78.43:30500/v1/kv/jwt_config?raw').text)


app.config.update(jwt_config)
jwt = JWTManager(app)

app.run(host='0.0.0.0', port=8000)