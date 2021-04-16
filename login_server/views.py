from json import dumps, loads
from flask import Response, jsonify, request, wrappers
from flask_restful import Resource, Api
from flask_jwt_extended import *
import mariadb

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


class SignUp(Resource):
    def post(self):
        json_data = request.get_json()
        login_id = json_data['id']
        login_pwd = json_data['pwd']
        sql = "INSERT INTO Users(login_id, login_password) " \
              "VALUES(?, ?)"
        cursor.execute(sql, [login_id, login_pwd])
        conn.commit()
        response_data = {
            'login_id': login_id
        }
        return Response(dumps(response_data), status=201, mimetype='application/json')


class Login(Resource):
    def post(self):
        json_data = request.get_json()
        login_id = json_data['id']
        login_pwd = json_data['pwd']
        sql = "SELECT user_id " \
              "FROM Users " \
              "WHERE login_id = ? AND login_password = ?"
        cursor.execute(sql, [login_id, login_pwd])
        user_id = get_fetchone_or_404()
        print(user_id)
        response_data = {
            "token": create_access_token(identity=user_id)
        }
        return Response(dumps(response_data), status=200, mimetype='application/json')