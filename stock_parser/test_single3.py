import requests
from bs4 import BeautifulSoup
import pymysql
from datetime import datetime, timedelta
import threading
import time
from kafka import KafkaProducer
from json import dumps
from json import loads
import consul

# consul kv 받아오기
c = consul.Consul(host='54.152.246.15', port=8500)
index = None

index, data = c.kv.get('db_config', index=index)
db_config = loads(data['Value'])
print(db_config)
# 주식번호
index, data = c.kv.get('stock_code3', index=index)
stock_code = loads(data['Value'])
print(stock_code)
# 주식번호
stock_id = 3

# 파싱해오는 실시간 주식 정보의 url과 헤더
url = 'https://finance.naver.com/item/sise_time.nhn?code={}&thistime={}&page={}'

header = {
    'User-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36"}

def stock_parser():

    producer = KafkaProducer(acks=0,
                         compression_type='gzip',
                         bootstrap_servers=['kafka:29092'],
                         value_serializer=lambda x: dumps(x).encode('utf-8')
                         )

    con = pymysql.connect(**db_config)
    cur = con.cursor()
    cur.execute(
        "SELECT updated_time FROM StockInfos WHERE stock_id='{}' ORDER BY updated_time DESC LIMIT 1".format(stock_id))
    try:
        exists_data = cur.fetchall()[0][0]
    except:
        exists_data = 0

    currentTime = "{:%Y%m%d%H%M%S}".format(datetime.now()+timedelta(hours=9))
    print(currentTime)
    parse_page = 100
    try:
        for page in range(1, parse_page):
            # 데이터 요청
            req = requests.get(url.format(
                stock_code, currentTime, page), headers=header)

        # 데이터 추출
            source = req.text
            soup = BeautifulSoup(source, 'html.parser')


            # 실시간 주가 추출
            for info in range(5):
                trade_price = soup.select(
                    'body > table.type2 > tr:nth-child({}) > td:nth-child(2) > span'.format(info+3))[0].text
                trade_price = int(trade_price.replace(',', ''))
                print(trade_price)

                # 현재시간 추출
                updated_time = soup.select(
                    'body > table.type2 > tr:nth-child({}) > td:nth-child(1) > span'.format(info+3))[0].text
                updated_time = updated_time.replace(':', '-')
                updated_time = "{:%Y-%m-%d-}{}".format(
                    datetime.now(), updated_time)

                if updated_time != exists_data:
                    #데이터스키마
                    data = {"schema": {"type": "struct", "fields": [{"type": "int32", "field": "stock_id"}, {"type": "int32", "field": "trade_price"}, {
                        "type": "string", "field": "updated_time"}], "name": "stockinfos"}, "payload": {"stock_id": stock_id, "trade_price": trade_price, "updated_time": updated_time}}

                    producer.send('StockInfos', value=data)
                    producer.flush()
                else:
                    break

            if updated_time==exists_data:
                break

            for info in range(5):
                trade_price = soup.select(
                    'body > table.type2 > tr:nth-child({}) > td:nth-child(2) > span'.format(info+11))[0].text
                trade_price = int(trade_price.replace(',', ''))
                print(trade_price)
                # 현재시간 추출
                updated_time = soup.select(
                    'body > table.type2 > tr:nth-child({}) > td:nth-child(1) > span'.format(info+11))[0].text
                updated_time = updated_time.replace(':', '-')
                updated_time = "{:%Y-%m-%d-}{}".format(
                    datetime.now(), updated_time)

                if updated_time != exists_data:
                    #데이터스키마
                    data = {"schema": {"type": "struct", "fields": [{"type": "int32", "field": "stock_id"}, {"type": "int32", "field": "trade_price"}, {
                        "type": "string", "field": "updated_time"}], "name": "stockinfos"}, "payload": {"stock_id": stock_id, "trade_price": trade_price, "updated_time": updated_time}}

                    producer.send('StockInfos', value=data)
                    producer.flush()
                else:
                    break

            if updated_time==exists_data:
                break
        print(stock_code, updated_time, 'jobs done')
    except:
        print('list index out of range but job is done')

    return "process ok"

# 쓰레드를 통해 반복 실행
def thread_parser(next_call_in):
    next_call_in += 60

    Time = "{:%H-%M}".format(datetime.now()+timedelta(hours=9))
    print(Time)
    if '15-30' > Time and '09-00' < Time:
        stock_parser()
    print('thread_parser running')
    threading.Timer(next_call_in - time.time(),
                    thread_parser,
                    [next_call_in]).start()


# 파싱
next_call_in = time.time()
thread_parser(next_call_in)