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


class SignUp(Resource):
    def post(self):
        json_data = request.get_json()
        login_id = json_data['id']
        login_pwd = json_data['pwd']
        email = json_data['email']
        sql = "INSERT INTO Users(login_id, login_password, email) " \
              "VALUES(?, ?, ?)"
        try:
            cursor.execute(sql, [login_id, login_pwd, email])
            conn.commit()
        except mariadb.IntegrityError:
            return Response(dumps({"message": "만들 수 없는 아이디입니다."}), status=200, mimetype='application/json')
        response_data = {
            "message": "생성되었습니다.",
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
        if type(user_id) is wrappers.Response:
            return user_id
        token = create_access_token(identity=user_id)
        headers = {
            "token": token
        }
        return Response(dumps({'message': 'success'}), headers=headers, status=200, mimetype='application/json')
