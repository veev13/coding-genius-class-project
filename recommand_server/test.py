from json import dumps, loads
from flask import Response, jsonify, request, wrappers
from flask_restful import Resource, Api
from flask_jwt_extended import *
import mariadb
from datetime import datetime, timedelta
import time

hour = int("{:%H}".format(datetime.now()))
if hour-5>0:
    for i in range(hour, , -1):
        , i)
        print(currentTime)
else:
    for i in range(hour, 0, -1):
        currentTime="{:%Y-%m-%d}-{}-00".format(datetime.now(), i)
        print(currentTime)


#print(datetime.now())
print(datetime.now()-timedelta(hours=1))

for i in range(5):
    Time="{:%Y-%m-%d-%H}-00".format(datetime.now()-timedelta(hours=i))
    