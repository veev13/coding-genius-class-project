from json import dumps, loads
from flask import Response, jsonify, request, render_template, redirect, url_for, make_response
import requests
from __init__ import app
import mariadb
from flask_jwt_extended import *

db_config = None
with open('../config/db_config.txt', 'r') as file:
    db_config_string = file.read()
    db_config = loads(db_config_string)

conn = mariadb.connect(**db_config)
cursor = conn.cursor()


def get_fetchone_or_404(error_message="잘못된 요청입니다."):
    try:
        return cursor.fetchone()[0]
    except:
        return Response(dumps({"message": error_message}), status=404, mimetype='application/json')

data = [
    ['04-06', 82000],
    ['04-07', 83000],
    ['04-08', 83200],
    ['04-09', 84500],
    ['04-10', 85000],
    ['04-11', 85500],
    ['04-12', 84300],
    ['04-13', 83000],
    ['04-14', 83500],
    ['04-15', 83200],
]
login_server = "http://localhost:5001"


@app.route('/')
def main_page():
    try:
        print(verify_jwt_in_request())
        logged_in = True
    except:
        logged_in = False
    token = request.cookies.get('access_token_cookie')
    print("쿠ㅋㅣ", token)
    chart_data = [['날짜', '거래가']] + data
    values = {'chart_data': chart_data,
              'logged_in': logged_in,
              }
    return render_template('index.html', values=values)


@app.route('/my')
def my_page():
    pass


@app.route('/login', methods=['POST'])
def login(signup=False):
    if request.method == 'POST':
        json_data = request.form
        login_res = requests.post(login_server + '/login', json=json_data)
        if login_res.status_code != 200:
            return render_template('login.html', signup=signup, token=None)
        jwt = login_res.headers['token']
        response = make_response(render_template('login.html', signup=signup, token=jwt))
        response.set_cookie("access_token_cookie", jwt)
        return response


@app.route('/logout', methods=['POST'])
def logout():
    res = make_response(redirect(url_for('main_page')))
    res.delete_cookie("access_token_cookie")
    return res


@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        json_data = request.form
        response = requests.post(login_server + '/signup', json=json_data)
        message = response.json()['message']
        if message:
            return render_template('signup.html', message=message)
        return login(signup=True)
