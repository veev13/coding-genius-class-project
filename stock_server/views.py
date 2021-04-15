from json import dumps, loads
from flask import Response, jsonify, request
from flask_restful import Resource, Api
from flask_restful import reqparse
import mariadb

db_config = None
with open('../config/db_config.txt', 'r') as file:
    db_config_string = file.read()
    db_config = loads(db_config_string)

conn = mariadb.connect(**db_config)
cursor = conn.cursor()


class StockBuy(Resource):
    def post(self):
        json_data = request.get_json()
        user_id = 1
        stock_id = json_data['stock_id']
        buy_count = json_data['count']

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
        trade_price = cursor.fetchone()[0]
        pay = trade_price * buy_count
        # 돈이 충분한 경우
        if pay <= point:
            point_update_sql = "UPDATE Users " \
                               "SET point = point - ? " \
                               "WHERE user_id = ?"
            cursor.execute(point_update_sql, [pay, user_id])
            # own_stock_check_sql = "SELECT user_id " \
            #                        "FROM Users_Stock " \
            #                        "WHERE user_id = ? AND stock_id = ?"
            try:
                own_stock_insert_sql = "INSERT INTO Users_Stock(user_id, stock_id, owning_numbers) " \
                                       "VALUES(?, ?, ?)"
                cursor.execute(own_stock_insert_sql, [user_id, stock_id, buy_count])
            except:
                own_stock_update_sql = "UPDATE Users_Stock " \
                                       "SET owning_numbers = owning_numbers + ? " \
                                       "WHERE user_id = ? AND stock_id = ?"
                cursor.execute(own_stock_update_sql, [buy_count, user_id, stock_id])
            conn.commit()
            return Response(dumps({"message": "success"}), status=201, mimetype='application/json')
        # 돈이 부족한 경우
        else:
            return Response(dumps({"message": "포인트가 부족합니다."}), status=200, mimetype='application/json')


class StockSell(Resource):
    def post(self):
        json_data = request.get_json()
        user_id = 1
        stock_id = json_data['stock_id']
        sell_count = json_data['count']

        get_own_count_sql = "SELECT owning_numbers " \
                            "FROM Users_Stock " \
                            "WHERE user_id = ? AND stock_id = ?"
        cursor.execute(get_own_count_sql, [user_id, stock_id])
        try:
            own_count = cursor.fetchone()[0]
        except:
            return Response(dumps({"message": "잘못된 요청입니다."}), status=404, mimetype='application/json')

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

        return Response(dumps({"message": "success"}), status=200, mimetype='application/json')


# 보유 종목 조회 API
class StockStatus(Resource):
    def get(self):
        # TODO: 유저 로그인 여부 확인 필요

        user_id = 1
        sql = "SELECT Users_Stock.stock_id, stock_name, feature, owning_numbers " \
              "FROM Users_Stock JOIN Stocks " \
              "WHERE user_id = ? AND Users_Stock.stock_id = Stocks.stock_id"
        cursor.execute(sql, [user_id])  # TODO: TEST, USER ID or TOKEN 입력 요함
        result_set = cursor.fetchall()
        row_header = [x[0] for x in cursor.description]
        json_data = []

        for result in result_set:
            json_data.append(dict(zip(row_header, result)))
        return Response(dumps(json_data), status=200, mimetype='application/json')


# 유저 보유 포인트 조회 API
class UserPoint(Resource):
    def get(self):
        # TODO: 유저 로그인 여부 확인 필요

        user_id = 1
        sql = "SELECT user_id, login_id, point " \
              "FROM Users " \
              "WHERE user_id = ?"
        cursor.execute(sql, [user_id])  # TODO: TEST, USER ID or TOKEN 입력 요함
        result = cursor.fetchone()
        row_header = [x[0] for x in cursor.description]
        json_data = dict(zip(row_header, result))
        return Response(dumps(json_data), status=200, mimetype='application/json')
