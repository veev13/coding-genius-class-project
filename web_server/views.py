from json import dumps, loads
<<<<<<< Updated upstream
from flask import Response, jsonify, request, render_template, redirect, url_for, make_response
import requests
from __init__ import app
from flask_jwt_extended import *
import pymysql
<<<<<<< HEAD
=======
from flask import Response, jsonify, request, render_template, make_response
from __init__ import app
=======
from flask import Response, jsonify, request, render_template, make_response
from __init__ import app
>>>>>>> Stashed changes
import pymysql
import numpy as np
=======
import re
>>>>>>> a9c801f227e48143e1b302f0bfce3f83d0bb6e77

db_config = None
<<<<<<< Updated upstream
with open('../config/db_config.txt', 'r') as file:
=======
>>>>>>> Stashed changes
with open('./config/db_config.txt', 'r') as file:
    db_config_string = file.read()
    db_config = loads(db_config_string)

conn = pymysql.connect(**db_config)
cursor = conn.cursor()
app.config["JSON_AS_ASCII"] = False

stock_server_host = 'http://127.0.0.1:5000/stocks'
user_server_host = 'http://127.0.0.1:5000/users'
login_server = "http://localhost:5001"


def get_fetchone_or_404(error_message="잘못된 요청입니다."):
    try:
        return cursor.fetchone()[0]
    except:
        return Response(dumps({"message": error_message}), status=404, mimetype='application/json')

<<<<<<< Updated upstream

def get_stock_chart_data(stock_code):
    sql = """
            SELECT updated_time,trade_price 
            FROM StockInfos 
            WHERE stock_id = %s
            """
    cursor.execute(sql, [stock_code])
    result = cursor.fetchall()
    result_data = []
    for a in result:
        data = []
        for b in a:
            data.append(b)
        result_data.append(data)

    chart_data = [['날짜', '거래가']] + result_data
    return chart_data


def get_stock_list():
    # 주식 목록 가져오기
    stock_list_res = requests.get(stock_server_host)
    if stock_list_res.status_code == 200:
        return stock_list_res.json()['stock_list']
    return []


def get_logged_in():
    try:
        verify_jwt_in_request()
        return True
    except:
        return False


@app.route('/')
def main_page():
    stock_name = '삼성전자'
    stock_code = '005930'
    values = {'chart_data': get_stock_chart_data(stock_code),
              'chart_name': stock_name,
              'logged_in': get_logged_in(),
              'stock_list': get_stock_list(),
              }
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
        "Authorization": "Bearer " + jwt,
    }
    my_stock_list_res = requests.get(user_server_host + '/stocks', headers=headers)
    values['my_stocks'] = []
    if my_stock_list_res.status_code == 200:
        my_stock_list = my_stock_list_res.json()
        values['my_stocks'] = my_stock_list

    my_point_res = requests.get(user_server_host + '/point', headers=headers)
    values['my_point'] = 0
    if my_point_res.status_code == 200:
        my_point = my_point_res.json()['point']
        values['my_point'] = my_point

    return render_template('mypage.html', values=values)


@app.route('/stock')
def stock_detail():
    stock = request.args.get('stock')

    bungi = stock.find('[')  # 분기점
    stock_name = stock[:bungi]
    stock_code = stock[bungi + 1:-1]
    values = {
        'chart_data': get_stock_chart_data(stock_code),
        'chart_name': stock_name,
        'chart_code': stock_code,
        'logged_in': get_logged_in(),
        'stock_list': get_stock_list(),
    }
    return render_template('stock.html', values=values)


@app.route('/stock/sell', methods=['get', 'post'])
def stock_sell():
    stock_id = request.args.get('id')
    stock_name = request.args.get('name')
    stock_price = request.args.get('price')
    if request.method == 'GET':
        values = {
            'trade_type': "매도",
            'stock_name': stock_name,
            'stock_id': stock_id,
            'trade_price': stock_price,
            'stock_list': get_stock_list(),
        }
        return render_template('stock_trade.html', values=values)
    else:
        jwt = request.cookies.get("access_token_cookie")
        get_logged_in()
        headers = {
            "Authorization": "Bearer " + jwt,
        }
        json_data = request.form
        trade_res = requests.post(stock_server_host + '/sell', json=json_data, headers=headers)
        message = trade_res.json()['message']
        return render_template('trade_ok.html', message=message)


@app.route('/stock/buy', methods=['get', 'post'])
def stock_buy():
    stock_id = request.args.get('id')
    stock_name = request.args.get('name')
    stock_price = request.args.get('price')
    if request.method == 'GET':
        values = {
            'trade_type': "매수",
            'stock_name': stock_name,
            'stock_id': stock_id,
            'trade_price': stock_price,
            'stock_list': get_stock_list(),
        }
        return render_template('stock_trade.html', values=values)
    else:
        jwt = request.cookies.get("access_token_cookie")
        get_logged_in()
        headers = {
            "Authorization": "Bearer " + jwt,
        }
        json_data = request.form
        trade_res = requests.post(stock_server_host + '/buy', json=json_data, headers=headers)
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
=======
>>>>>>> Stashed changes
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
@app.route('/')
def main_page():
    chart_data = [['날짜', '거래가']] + data
    values = {'chart_data': chart_data}
    return render_template('index.html', values=values)

# @app.route("/test")
# def test():
#     sql = """
#     select updated_time, trade_price from StockInfos
#     """
#     cursor.execute(sql)
#     result = cursor.fetchall()
#     # print(len(result))
#     # print(result[0][0])
#     # return result
