from json import dumps, loads
from flask import Response, jsonify, request, render_template
from __init__ import app
import pymysql

db_config = None
with open('./config/db_config.txt', 'r') as file:
    db_config_string = file.read()
    db_config = loads(db_config_string)

conn = pymysql.connect(**db_config)
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


@app.route('/')
def main_page():
    sql = """
    select updated_time,trade_price from StockInfos
    """
    cursor.execute(sql)
    result = cursor.fetchall()
    # print(list(result[160]))

    # for a in range(lenresult:
    #     chart_data = list(result[a])

    # print(chart_data[167])

    chart_data = []

    data = []
    result_data = []
    for a in result:
        # print(a)
        data = []
        for b in a:
            data.append(b)
        result_data.append(data)
    print(result_data)

    chart_data = [['날짜', '거래가']] + result_data
    values = {'chart_data': chart_data}
    return render_template('index.html', values=values)
