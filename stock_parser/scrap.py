import requests
from bs4 import BeautifulSoup
import pymysql
from datetime import datetime
from json import loads

# 현재시간
currentTime = "{:%Y%m%d%H%M%S}".format(datetime.now())

# 파싱해오는 실시간 주식 정보의 url과 헤더
# url에 code부분에 format{}로 코드값을 받아줌
url = 'https://finance.naver.com/item/sise_time.nhn?code={}&thistime={}&page={}'

header = {
    'User-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36"}

# db config
db_config = {}
with open('../config/db_config.txt', 'r') as file:
    db_config = loads(file.read())


# db삽입
def stock_quary(stock_code, trade_price, update_Time):
    con = pymysql.connect(**db_config)
    cur = con.cursor()

    cur.execute("SELECT updated_time FROM StockInfos WHERE updated_time='{}'".format(update_Time))
    exists_data = cur.fetchall()
    if not exists_data:
        sql = "INSERT INTO StockInfos(stock_id,trade_price,updated_time) VALUES('{}',{},'{}')"

        sql = sql.format(stock_code, trade_price, update_Time)

        cur.execute(sql)
        con.commit()

    print(update_Time + 'quary success')
    return 0


# 문자열로 주식코드가 전달
def stock_parser(stock_code):
    for page in range(1, 3):
        # 데이터 요청
        req = requests.get(url.format(stock_code, currentTime, page), headers=header)

        # 데이터 추출
        source = req.text
        soup = BeautifulSoup(source, 'html.parser')

        # 실시간 주가 추출
        for info in range(5):
            trade_price = \
            soup.select('body > table.type2 > tr:nth-child({}) > td:nth-child(2) > span'.format(info + 3))[0].text
            trade_price = trade_price.replace(',', '')

            # 현재시간 추출
            updated_time = \
            soup.select('body > table.type2 > tr:nth-child({}) > td:nth-child(1) > span'.format(info + 3))[0].text
            updated_time = updated_time.replace(':', '-')
            updated_time = "{:%Y-%m-%d-}{}".format(datetime.now(), updated_time)
            stock_quary(stock_code, trade_price, updated_time)

        for info in range(5):
            trade_price = \
            soup.select('body > table.type2 > tr:nth-child({}) > td:nth-child(2) > span'.format(info + 11))[0].text
            trade_price = trade_price.replace(',', '')

            # 현재시간 추출
            updated_time = \
            soup.select('body > table.type2 > tr:nth-child({}) > td:nth-child(1) > span'.format(info + 11))[0].text
            updated_time = updated_time.replace(':', '-')
            updated_time = "{:%Y-%m-%d-}{}".format(datetime.now(), updated_time)
            stock_quary(stock_code, trade_price, updated_time)

    # 현재시간 추출
    updated_time = soup.select('body > table.type2 > tr:nth-child(3) > td:nth-child(1) > span')[0].text
    updated_time = updated_time.replace(':', '')

    # 실시간 주식 가격 반환
    return 0


# 테스트 출력
stock_code = '000660'

stock_parser(stock_code)
