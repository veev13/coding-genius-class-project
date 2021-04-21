import requests
from bs4 import BeautifulSoup
import pymysql
from datetime import datetime 
import threading
import time
from kafka import KafkaProducer
from json import dumps


# 현재시간


# 파싱해오는 실시간 주식 정보의 url과 헤더
# url에 code부분에 format{}로 코드값을 받아줌
url= 'https://finance.naver.com/item/sise_time.nhn?code={}&thistime={}&page={}'

header= {'User-agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36"}

producer = KafkaProducer(acks=0,
                         compression_type='gzip',
                         bootstrap_servers=['127.0.0.1:9092'],
                         value_serializer=lambda x: dumps(x).encode('utf-8')
                         )


currentTime="{:%Y%m%d%H%M%S}".format(datetime.now())
stock_code='005930'
req = requests.get(url.format(stock_code,currentTime,1), headers=header)

        # 데이터 추출
source = req.text
soup = BeautifulSoup(source, 'html.parser')
# for info in range(5):
trade_price = soup.select('body > table.type2 > tr:nth-child({}) > td:nth-child(2) > span'.format(1+11))[0].text
trade_price = int(trade_price.replace(',',''))

# 현재시간 추출
updated_time = soup.select('body > table.type2 > tr:nth-child({}) > td:nth-child(1) > span'.format(1+11))[0].text
updated_time = updated_time.replace(':','-')
updated_time="{:%Y-%m-%d-}{}".format(datetime.now(),updated_time)


# data = {"schema": {"type": "struct", "fields": [{"type": "int32", "field": "stock_info_id"},{"type": "string", "field": "stock_id"}, {"type": "int32", "field": "trade_price"}, {"type": "string", "field": "updated_time"}], "name": "stockinfos"}, "payload": {"stock_info_id":5,"stock_id": stock_code, "trade_price": trade_price, "updated_time": updated_time}}
data = {"schema": {"type": "struct", "fields": [{"type": "string", "field": "stock_id"}, {"type": "int32", "field": "trade_price"}, {"type": "string", "field": "updated_time"}], "name": "stockinfos"}, "payload": {"stock_id": stock_code, "trade_price": trade_price, "updated_time": updated_time}}
producer.send('StockInfos', value=data)
producer.flush()

                    
           

                
           

# # 쓰레드를 통해 반복 실행
# def thread_parser(next_call_in):
#     next_call_in +=60

#     stock_parser()
    
#     threading.Timer(next_call_in - time.time(),
#                     thread_parser,
#                     [next_call_in]).start()


