from json import dumps, loads
from flask import Response, jsonify, request, render_template, redirect, url_for, make_response
import requests
from __init__ import app
from flask_jwt_extended import *
import pymysql
import consul

import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from config import hosts

c = consul.Consul(host='54.152.246.15', port=8500)
index = None

index, data = c.kv.get('db_config', index=index)
db_config = loads(data['Value'])
conn = pymysql.connect(**db_config)
cursor = conn.cursor()
app.config["JSON_AS_ASCII"] = False

stock_server_host = hosts.hosts.stock_server_service
user_server_host = hosts.hosts.users_server_service
login_server = hosts.hosts.login_server_service


def get_fetchone_or_404(error_message="잘못된 요청입니다."):
    try:
        return cursor.fetchone()[0]
    except:
        return Response(dumps({"message": error_message}), status=404, mimetype='application/json')


def get_stock_chart_data(stock_code):
    chart_res = requests.get(stock_server_host + f'/chart?code={stock_code}')
    if chart_res.status_code == 200:
        return chart_res.json()['chart_data'], chart_res.json()['chart_name']
    else:
        return chart_res.json()['message'], "NULL"


def get_stock_list():
    # 주식 목록 가져오기
    try:
        stock_list_res = requests.get(stock_server_host)
        if stock_list_res.status_code == 200:
            return stock_list_res.json()['stock_list']
    except:
        return []


def get_logged_in():
    try:
        verify_jwt_in_request()
        return True
    except:
        return False


@app.route('/')
def main_page():
    recommand_res = requests.get(hosts.hosts.recommand_server_service + "/recommand")

    stock_code = recommand_res.json()['max']

    values = {
        'logged_in': get_logged_in(),
        'stock_list': get_stock_list(),
    }
    chart_data, chart_name = get_stock_chart_data(stock_code)
    if not type(chart_data) == str:
        if len(chart_data) == 1:
            values['message'] = "데이터가 없습니다."
        else:
            values['chart_data'] = chart_data
            values['chart_name'] = chart_name
    else:
        values['message'] = chart_data
    return render_template('index.html', values=values)


@app.route('/point/charge')
def copy_point():
    if get_logged_in():
        point = request.args.get('add')
        user_id = get_jwt_identity()
        # SQL injection 위험

        sql = "UPDATE Users " \
              f"SET point = point + {point} " \
              f"WHERE user_id = {user_id}"
        cursor.execute(sql)
        conn.commit()
    return redirect(url_for('main_page'))


@app.route('/mypage')
def my_page():
    jwt = request.cookies.get("access_token_cookie")
    values = {
        'logged_in': get_logged_in(),
        'stock_list': get_stock_list(),
    }
    headers = {
        "Authorization": "Bearer " + (jwt if jwt else ""),
    }
    my_stock_list_res = requests.get(
        user_server_host + '/stocks', headers=headers)
    values['my_stocks'] = []
    if my_stock_list_res.status_code == 200:
        my_stock_list = my_stock_list_res.json()
        values['my_stocks'] = my_stock_list

    my_point_res = requests.get(user_server_host + '/point', headers=headers)
    values['my_point'] = 0
    if my_point_res.status_code == 200:
        my_point = my_point_res.json()['point']
        values['my_point'] = my_point
    values['stock_list'] = get_stock_list()

    return render_template('mypage.html', values=values)


@app.route('/alarm', methods=['post'])
def stock_alarm():
    jwt = request.cookies.get("access_token_cookie")
    json_data = request.form
    headers = {
        "Authorization": "Bearer " + (jwt if jwt else ""),
    }
    alarm_set_res = requests.post(stock_server_host + '/alarms', json=json_data, headers=headers)
    if alarm_set_res.status_code == 201:
        message = alarm_set_res.json()['message']
    else:
        message = "잘못된 접근입니다."

    return render_template('message.html', message=message)


@app.route('/stock')
def stock_detail():
    stock = request.args.get('stock')

    bungi = stock.find('[')  # 분기점
    stock_name = stock[:bungi]
    stock_code = stock[bungi + 1:-1]
    values = {
        'chart_name': stock_name,
        'chart_code': stock_code,
        'logged_in': get_logged_in(),
        'stock_list': get_stock_list(),
    }
    chart_data, chart_name = get_stock_chart_data(stock_code)
    if not type(chart_data) == str:
        if len(chart_data) == 1:
            values['message'] = "데이터가 없습니다."
        else:
            values['chart_data'] = chart_data
    else:
        values['message'] = chart_data
    return render_template('stock.html', values=values)


@app.route('/stock/sell', methods=['get', 'post'])
def stock_sell():
    stock_code = request.args.get('code')
    stock_name = request.args.get('name')
    stock_price = request.args.get('price')
    if request.method == 'GET':
        values = {
            'trade_type': "매도",
            'stock_name': stock_name,
            'stock_code': stock_code,
            'trade_price': stock_price,
            'stock_list': get_stock_list(),
        }
        return render_template('stock_trade.html', values=values)
    else:
        jwt = request.cookies.get("access_token_cookie")
        get_logged_in()
        headers = {
            "Authorization": "Bearer " + (jwt if jwt else ""),
        }
        json_data = request.form
        trade_res = requests.post(
            stock_server_host + '/sell', json=json_data, headers=headers)
        message = trade_res.json()['message']
        return render_template('trade_ok.html', message=message)


@app.route('/stock/buy', methods=['get', 'post'])
def stock_buy():
    stock_code = request.args.get('code')
    stock_name = request.args.get('name')
    stock_price = request.args.get('price')
    if request.method == 'GET':
        values = {
            'trade_type': "매수",
            'stock_name': stock_name,
            'stock_code': stock_code,
            'trade_price': stock_price,
            'stock_list': get_stock_list(),
        }
        return render_template('stock_trade.html', values=values)
    else:
        jwt = request.cookies.get("access_token_cookie")
        get_logged_in()
        headers = {
            "Authorization": "Bearer " + (jwt if jwt else ""),
        }
        json_data = request.form
        trade_res = requests.post(
            stock_server_host + '/buy', json=json_data, headers=headers)
        message = trade_res.json()['message']
        return render_template('trade_ok.html', message=message)


@app.route('/login', methods=['POST'])
def login(signup=False):
    if request.method == 'POST':
        json_data = request.form
        login_res = requests.post(login_server + '/login', json=json_data)
        if login_res.status_code != 200:
            return render_template('login.html', signup=signup, token=None)
        jwt = login_res.headers['token']
        response = make_response(render_template(
            'login.html', signup=signup, token=jwt))
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
        print(response.json())
        message = response.json()['message']
        return render_template('message.html', message=message)
