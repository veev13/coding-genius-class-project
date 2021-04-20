import requests
from bs4 import BeautifulSoup
import pymysql
from datetime import datetime 
import threading
import time


# 현재시간


# 파싱해오는 실시간 주식 정보의 url과 헤더
# url에 code부분에 format{}로 코드값을 받아줌
url= 'https://finance.naver.com/item/sise_time.nhn?code={}&thistime={}&page={}'

header= {'User-agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36"}


# db config
db_config = {}
with open('../config/db_config.txt', 'r') as file:
    db_config = loads(file.read())



# db삽입
def stock_query(stock_code, trade_price, updated_time):
    con = pymysql.connect(**db_config)
    cur= con.cursor()

    cur.execute("SELECT updated_time FROM StockInfos WHERE updated_time='{}' AND stock_id='{}'".format(updated_time, stock_code))
    exists_data = cur.fetchall()
    if not exists_data:
        sql= "INSERT INTO StockInfos(stock_id,trade_price,updated_time) VALUES('{}',{},'{}')"
        
        sql=sql.format(stock_code,trade_price,updated_time)

        cur.execute(sql)
        con.commit()
        print(updated_time+'query success')
    else: return 1
    
    
    return 0

# 문자열로 주식코드가 전달
def stock_parser():

    con = pymysql.connect(**config)
    cur = con.cursor()
    # 주식코드 가져오기
    cur.execute("SELECT stock_id FROM Stocks")
    stock_codes_all = cur.fetchall()
    
    currentTime="{:%Y%m%d%H%M%S}".format(datetime.now())

    for stock_codes in stock_codes_all:
        
        stock_code=stock_codes[0]

        parse_page=500
        try:
            for page in range(1,parse_page):
            # 데이터 요청 
                req = requests.get(url.format(stock_code,currentTime,page), headers=header)

            # 데이터 추출
                source = req.text
                soup = BeautifulSoup(source, 'html.parser')
                
                # 실시간 주가 추출
                for info in range(5):
                    trade_price = soup.select('body > table.type2 > tr:nth-child({}) > td:nth-child(2) > span'.format(info+3))[0].text
                    trade_price = trade_price.replace(',','')

                    # 현재시간 추출
                    updated_time = soup.select('body > table.type2 > tr:nth-child({}) > td:nth-child(1) > span'.format(info+3))[0].text
                    updated_time = updated_time.replace(':','-')
                    updated_time="{:%Y-%m-%d-}{}".format(datetime.now(),updated_time)

                    # 중복데이터 확인
                    cur.execute("SELECT updated_time FROM StockInfos WHERE updated_time='{}' AND stock_id='{}'".format(updated_time, stock_code))
                    exists_data = cur.fetchall()
                    if not exists_data:
                        stock_query(stock_code,trade_price,updated_time)
                    else: break

                if exists_data:
                    break

                for info in range(5):
                    trade_price = soup.select('body > table.type2 > tr:nth-child({}) > td:nth-child(2) > span'.format(info+11))[0].text
                    trade_price = trade_price.replace(',','')

                    # 현재시간 추출
                    updated_time = soup.select('body > table.type2 > tr:nth-child({}) > td:nth-child(1) > span'.format(info+11))[0].text
                    updated_time = updated_time.replace(':','-')
                    updated_time="{:%Y-%m-%d-}{}".format(datetime.now(),updated_time)
                    cur.execute("SELECT updated_time FROM StockInfos WHERE updated_time='{}' AND stock_id='{}'".format(updated_time, stock_code))
                    exists_data = cur.fetchall()
                    if not exists_data:
                        stock_query(stock_code,trade_price,updated_time)
                    else: break

                if exists_data:
                    break
            print(stock_code,'jobs done')

        except: print(stock_code,'jobs done')

    # 실시간 주식 가격 반환
    return 0

# 쓰레드를 통해 반복 실행
def thread_parser(next_call_in):
    next_call_in +=60

    stock_parser()
    
    threading.Timer(next_call_in - time.time(),
                    thread_parser,
                    [next_call_in]).start()


# 테스트 출력
next_call_in = time.time()
thread_parser(next_call_in)




