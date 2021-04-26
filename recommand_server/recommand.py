import requests
import pymysql
from datetime import datetime, timedelta
import threading
import time
from json import dumps
from json import loads
import consul

# consul kv 받아오기
c = consul.Consul(host='54.152.246.15', port=8500)
index = None

index, data = c.kv.get('recommand_db_config', index=index)
recommand_db_config = loads(data['Value'])

def weather_sort(weather):
    # 리스트 두 개 받아서 짜기(날씨데이터 5개, 주식데이터 5개)
    weather_list = []
    num = 0

    for i in reversed(weather):

        if num < 5:
            weather_list.append(i)
            num += 1
        else:
            break

    # print(weather_list)
    weather_rate = []

    for index in range(len(weather_list)):
        try:
            prev = weather_list[index]
            pre = weather_list[index+1]
            rate = ((prev - pre) / prev)*100
            weather_rate.append(round(rate,2))

        except:
            break

    return weather_rate


def stock_sort(price_list):
    price_re = []
    for index in price_list:
        price_re.append(index)

    price_rate = []
    for i in range(len(price_re)):
        try:
            prev = price_re[i]
            pre = price_re[i+1]
            rate = ((prev - pre) / prev)*100
            price_rate.append(round(rate,2))

        except:
            break

    print(price_rate,'a')
    return price_rate


def recommand(weather_rate, price_rate):
    similarity = 0
    for idx in range(len(price_rate)):
        similarity += abs(weather_rate[idx] - price_rate[idx])
    similarity = round(similarity, 2)
    return similarity



def insert_rec(stock_id, similarity):
    
    conn = pymysql.connect(**recommand_db_config)
    cursor = conn.cursor()

 
    sql = """
    INSERT INTO Recommands (stock_id,similarity) VALUES('{}',{})
    """
    sql = sql.format(stock_id, similarity)

    cursor.execute(sql)
    conn.commit()
    print('query added')
    conn.close()

def recommand_do():
    url = "SELECT temp FROM Weathers order by rand() LIMIT 5"
    con = pymysql.connect(**recommand_db_config)
    cur = con.cursor()
    cur.execute(url)
    weather=[]    ### 중요한거     
    weather_data = cur.fetchall()
    for temps in weather_data:
        weather.append(temps[0])


    for stock_id in range(1,6):
        price_list=[]
        url = "SELECT trade_price FROM StockInfos Where stock_id={} order by rand() LIMIT 5".format(stock_id)
        cur.execute(url)
        price_data = cur.fetchall()
        for price in price_data:
            price_list.append(price[0])

        insert_rec(stock_id, recommand(weather_sort(weather),stock_sort(price_list)))


# 쓰레드를 통해 반복 실행
def thread_parser(next_call_in):
    next_call_in += 3600*24
    
    recommand_do()
    print('thread_parser running')
    threading.Timer(next_call_in - time.time(),
                    thread_parser,
                    [next_call_in]).start()


next_call_in = time.time()
thread_parser(next_call_in)




