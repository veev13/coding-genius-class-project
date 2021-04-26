from json import dumps, loads
from flask import Response, jsonify, request, wrappers
from flask_restful import Resource, Api
from flask_jwt_extended import *
import mariadb
import consul

c = consul.Consul(host='54.152.246.15', port=8500)
index = None

index, data = c.kv.get('db_config', index=index)
db_config = loads(data['Value'])

conn = mariadb.connect(**db_config)
cursor = conn.cursor()


def get_fetchone_or_404(error_message="잘못된 요청입니다."):
    try:
        return cursor.fetchone()[0]
    except:
        return Response(dumps({"message": error_message}), status=404, mimetype='application/json')


def get_stock_id_by_stock_code(stock_code):
    # Stock Code to Stock ID
    sql = "SELECT stock_id, stock_name " \
          "FROM Stocks " \
          "WHERE stock_code = ?"
    cursor.execute(sql, [stock_code])
    try:
        return cursor.fetchone()
    except:
        return Response(dumps({"message": "존재하지 않는 종목입니다."}), status=404, mimetype='application/json'), "NULL"


class StockChartData(Resource):
    def get(self):
        stock_code = request.args.get('code')
        stock_id, stock_name = get_stock_id_by_stock_code(stock_code)
        if type(stock_id) is wrappers.Response:
            return Response(dumps({"message": "존재하지 않는 종목입니다."}), status=404, mimetype='application/json')
        sql = """
                    SELECT updated_time,trade_price 
                    FROM StockInfos 
                    WHERE stock_id = %s 
                    ORDER BY updated_time
                    """
        cursor.execute(sql, [stock_id])
        result = cursor.fetchall()
        result_data = []
        for a in result:
            data = []
            for b in a:
                data.append(b)
            result_data.append(data)

        chart_data = [['날짜', '거래가']] + result_data
        return Response(dumps({"chart_data": chart_data,
                               "chart_name": stock_name,
                               }), status=200, mimetype='application/json')


class StockBuy(Resource):
    @jwt_required()
    def post(self):
        json_data = request.get_json()
        user_id = get_jwt_identity()
        stock_code = json_data['stock_code']
        buy_count = int(json_data['count'])

        stock_id, stock_name = get_stock_id_by_stock_code(stock_code)
        if type(stock_id) is wrappers.Response:
            return stock_id

        # 보유 포인트 확인
        get_user_point_sql = "SELECT point " \
                             "FROM Users " \
                             "WHERE user_id = ?"
        cursor.execute(get_user_point_sql, [user_id])
        point = cursor.fetchone()[0]

        get_stock_price_sql = "SELECT trade_price " \
                              "FROM StockInfos " \
                              "WHERE stock_id = ? " \
                              "ORDER BY updated_time DESC " \
                              "LIMIT 1"
        cursor.execute(get_stock_price_sql, [stock_id])
        trade_price = get_fetchone_or_404()
        if type(trade_price) is wrappers.Response:
            return trade_price
        pay = trade_price * buy_count
        # 돈이 충분한 경우
        if pay <= point:
            point_update_sql = "UPDATE Users " \
                               "SET point = point - ? " \
                               "WHERE user_id = ?"
            cursor.execute(point_update_sql, [pay, user_id])
            try:
                own_stock_insert_sql = "INSERT INTO Users_Stock(user_id, stock_id, owning_numbers) " \
                                       "VALUES(?, ?, ?)"
                cursor.execute(own_stock_insert_sql, [
                    user_id, stock_id, buy_count])
            except:
                own_stock_update_sql = "UPDATE Users_Stock " \
                                       "SET owning_numbers = owning_numbers + ? " \
                                       "WHERE user_id = ? AND stock_id = ?"
                cursor.execute(own_stock_update_sql, [
                    buy_count, user_id, stock_id])
            conn.commit()
            return Response(dumps({"message": f"거래가 완료되었습니다. 현재 보유 포인트: {point - pay}"}), status=201,
                            mimetype='application/json')
        # 돈이 부족한 경우
        else:
            return Response(dumps({"message": "포인트가 부족합니다."}), status=200, mimetype='application/json')


class StockSell(Resource):
    @jwt_required()
    def post(self):
        json_data = request.get_json()
        user_id = get_jwt_identity()
        stock_code = json_data['stock_code']
        sell_count = int(json_data['count'])

        stock_id = get_stock_id_by_stock_code(stock_code)
        if type(stock_id) is wrappers.Response:
            return stock_id

        get_own_count_sql = "SELECT owning_numbers " \
                            "FROM Users_Stock " \
                            "WHERE user_id = ? AND stock_id = ?"
        cursor.execute(get_own_count_sql, [user_id, stock_id])

        own_count = get_fetchone_or_404()
        if type(own_count) is wrappers.Response:
            return own_count

        # 보유 주식 갯수 < 팔려는 갯수인 경우
        if sell_count > own_count:
            return Response(dumps({"message": "보유 주식의 갯수가 부족합니다."}), status=404, mimetype='application/json')

        get_stock_price_sql = "SELECT trade_price " \
                              "FROM StockInfos " \
                              "WHERE stock_id = ? " \
                              "ORDER BY updated_time DESC " \
                              "LIMIT 1"
        cursor.execute(get_stock_price_sql, [stock_id])
        trade_price = cursor.fetchone()[0]

        stock_selling_sql = "UPDATE Users_Stock " \
                            "SET owning_numbers = owning_numbers - ? " \
                            "WHERE user_id = ? AND stock_id = ?"
        cursor.execute(stock_selling_sql, [sell_count, user_id, stock_id])
        point_update_sql = "UPDATE Users " \
                           "SET point = point + ? " \
                           "WHERE user_id = ?"
        cursor.execute(point_update_sql, [sell_count * trade_price, user_id])
        conn.commit()

        return Response(dumps({"message": f"거래가 완료되었습니다. 현재 보유 주식: {own_count - sell_count}"}), status=200,
                        mimetype='application/json')


# 보유 종목 조회 API
class StockStatus(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        sql = "SELECT stock_code, stock_name, feature, owning_numbers " \
              "FROM Users_Stock JOIN Stocks " \
              "WHERE user_id = ? AND Users_Stock.stock_id = Stocks.stock_id"
        cursor.execute(sql, [user_id])
        result_set = cursor.fetchall()
        row_header = [x[0] for x in cursor.description]
        json_data = []

        for result in result_set:
            json_data.append(dict(zip(row_header, result)))
        return Response(dumps(json_data), status=200, mimetype='application/json')


# 유저 보유 포인트 조회 API
class UserPoint(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        sql = "SELECT user_id, login_id, point " \
              "FROM Users " \
              "WHERE user_id = ?"
        cursor.execute(sql, [user_id])
        result = cursor.fetchone()
        row_header = [x[0] for x in cursor.description]
        json_data = dict(zip(row_header, result))
        return Response(dumps(json_data), status=200, mimetype='application/json')


# 알람 설정 API
class StockAlarms(Resource):
    @jwt_required()
    def post(self):
        json_data = request.get_json()
        user_id = get_jwt_identity()
        stock_code = json_data['stock_code']
        sql = "SELECT stock_id FROM Stocks WHERE stock_code = ?"
        cursor.execute(sql, [stock_code])
        stock_id = get_fetchone_or_404("존재하지 않는 종목입니다.")
        if type(stock_id) is wrappers.Response:
            return stock_id

        price = json_data['price']
        condition_type = json_data['condition_type']

        # 알람 설정을 db에 저장
        try:
            sql = "INSERT INTO Alarms(user_id, stock_id, price, condition_type) " \
                  "VALUES(?, ?, ?, ?)"
            cursor.execute(sql, [user_id, stock_id, price, condition_type])
            conn.commit()

        # 이미 설정된 종목을 다시 설정할 때 예외처리
        except mariadb.IntegrityError:
            sql = "UPDATE Alarms " \
                  "SET price = ?, condition_type = ? " \
                  "WHERE user_id = ? AND stock_id = ?"
            cursor.execute(sql, [price, condition_type, user_id, stock_id])
            conn.commit()

        return Response(dumps({"message": "알람이 설정되었습니다."}), status=201, mimetype='application/json')


# 주식 목록 조회 API
class StockList(Resource):
    def get(self):
        sql = "SELECT *" \
              "FROM Stocks "
        cursor.execute(sql)
        result_set = cursor.fetchall()
        row_header = [x[0] for x in cursor.description]
        json_data = []
        for result in result_set:
            json_data.append(dict(zip(row_header, result)))
        return Response(dumps({"stock_list": json_data}), status=200, mimetype='application/json')
