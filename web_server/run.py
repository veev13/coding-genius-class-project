from views import app
from flask_jwt_extended import *
from json import loads
import consul

c = consul.Consul(host='3.237.78.43', port=30500)
index = None
index, data = c.kv.get('jwt_config', index=index)
jwt_config = loads(data['Value'])

app.config.update(jwt_config)
jwt = JWTManager(app)

app.run(host='0.0.0.0', port=8000)