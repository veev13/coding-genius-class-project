import requests
from bs4 import BeautifulSoup
import pymysql
from datetime import datetime 
import threading
import time
from kafka import KafkaProducer
from json import dumps
from json import loads

db_config={}

db_config=loads(requests.get('http://localhost:8500/v1/kv/db_config?raw').text)

stock_code=requests.get('http://localhost:8500/v1/kv/stock_code1?raw').text

print(stock_code)

# 문자열로 주식코드가 전달


    
        
# con = pymysql.connect(**db_config)
# cur = con.cursor()

# cur.execute("SELECT stock_id FROM Stocks")
# exists_data = cur.fetchall()
# print(exists_data)
    