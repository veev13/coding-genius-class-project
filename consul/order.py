
from flask import Flask
import requests
import os

app = Flask(__name__)


@app.route('/')
def get_order():
    url = os.environ.get('INV_SVC_URL')
    response = requests.get(url)
    ver = "1.0"
    res = '{"Service":"Order", "Version":' + ver + '}\n'
    res = res + response.content.decode('utf-8')
    return res


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
