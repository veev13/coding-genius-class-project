import requests
from bs4 import BeautifulSoup
import pymysql
from datetime import datetime 
import threading
import time
from kafka import KafkaProducer
from json import dumps
from json import loads

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

stock_code='035420'

db_config = {}
with open('../config/db_config.txt', 'r') as file:
    db_config = loads(file.read())

# 문자열로 주식코드가 전달
def stock_parser():

    
        
    con = pymysql.connect(**db_config)
    cur = con.cursor()
    # 주식코드 가져오기
    # cur.execute("SELECT stock_id FROM Stocks")
    # stock_codes_all = cur.fetchall()
    

    currentTime="{:%Y%m%d%H%M%S}".format(datetime.now())

    parse_page=500
    # try:
    # 중복확인용 데이터 가져오기
    cur.execute("SELECT updated_time FROM StockInfos WHERE stock_id='{}' ORDER BY updated_time DESC LIMIT 1".format(stock_code))
    try:
        exists_data = cur.fetchall()[0]
    except:
        exists_data = 0
    
    

    for page in range(1,parse_page):
    # 데이터 요청 
        req = requests.get(url.format(stock_code,currentTime,page), headers=header)

    # 데이터 추출
        source = req.text
        soup = BeautifulSoup(source, 'html.parser')
        
        # 실시간 주가 추출
        for info in range(5):
            trade_price = soup.select('body > table.type2 > tr:nth-child({}) > td:nth-child(2) > span'.format(info+3))[0].text
            trade_price = int(trade_price.replace(',',''))

            # 현재시간 추출
            updated_time = soup.select('body > table.type2 > tr:nth-child({}) > td:nth-child(1) > span'.format(info+3))[0].text
            updated_time = updated_time.replace(':','-')
            updated_time="{:%Y-%m-%d-}{}".format(datetime.now(),updated_time)

            if updated_time != exists_data:
                
                data = {"schema": {"type": "struct", "fields": [{"type": "string", "field": "stock_id"}, {"type": "int32", "field": "trade_price"}, {"type": "string", "field": "updated_time"}], "name": "stockinfos"}, "payload": {"stock_id": stock_code, "trade_price": trade_price, "updated_time": updated_time}}
                
                producer.send('StockInfos', value=data)
                producer.flush()
            else: break

        if exists_data:
            break

        for info in range(5):
            trade_price = soup.select('body > table.type2 > tr:nth-child({}) > td:nth-child(2) > span'.format(info+11))[0].text
            trade_price = int(trade_price.replace(',',''))

            # 현재시간 추출
            updated_time = soup.select('body > table.type2 > tr:nth-child({}) > td:nth-child(1) > span'.format(info+11))[0].text
            updated_time = updated_time.replace(':','-')
            updated_time="{:%Y-%m-%d-}{}".format(datetime.now(),updated_time)
            
            if  updated_time != exists_data:
                data = {"schema": {"type": "struct", "fields": [{"type": "string", "field": "stock_id"}, {"type": "int32", "field": "trade_price"}, {"type": "string", "field": "updated_time"}], "name": "stockinfos"}, "payload": {"stock_id": stock_code, "trade_price": trade_price, "updated_time": updated_time}}

                producer.send('StockInfos', value=data)
                producer.flush()
            else: break

        if exists_data:
            break
    print(stock_code, updated_time, 'jobs done')

    # except : print(stock_code, 'jobs except')

    # 실시간 주식 가격 반환
    return 0

# 쓰레드를 통해 반복 실행
def thread_parser(next_call_in):
    next_call_in +=60

    Time="{:%H-%M}".format(datetime.now())

    if '15-30'>Time and '09-00'<Time:
        stock_parser()
    
    threading.Timer(next_call_in - time.time(),
                    thread_parser,
                    [next_call_in]).start()


# 테스트 출력
print("파싱시작")
next_call_in = time.time()
thread_parser(next_call_in)