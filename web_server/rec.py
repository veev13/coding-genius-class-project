import pymysql
from json import dumps, loads
from datetime import datetime


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
            weather_rate.append(rate)

        except:
            break

    return weather_rate


def stock_sort(stock_id, price_list):
    price_re = []
    for index in price_list:
        price_re.append(index)

    price_rate = []
    for i in range(len(price_re)):
        try:
            prev = price_re[i]
            pre = price_re[i+1]
            rate = ((prev - pre) / prev)*100
            price_rate.append(rate)

        except:
            break

    print(price_rate)
    return price_rate


def recommand(weather_rate, price_rate):
    total = 0
    for idx in range(len(price_rate)):
        total = weather_rate[idx] - price_rate[idx]
    total = round(total, 2)
    return total


def insert_rec(stock_code, total):
    db_config=loads(requests.get('http://localhost:8500/v1/kv/db_config?raw').text)


    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()

 
    
    sql = """
    INSERT INTO Recommands (stock_id,similarity) VALUES('{}',{})
    """
    sql = sql.format(stock_code, total)

    cursor.execute(sql)
    conn.commit()
    print('query added')
    conn.close()


def get_max():

    db_config=loads(requests.get('http://localhost:8500/v1/kv/db_config?raw').text) 

    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()

    max = """
    SELECT MAX(similarity) FROM Recommands ORDER BY updated_time DESC LIMIT 10
    """

    cursor.execute(max)

    diff = cursor.fetchone()
    diff = list(diff)

    # print(diff[0])
    return max

def get_min():

    db_config=loads(requests.get('http://localhost:8500/v1/kv/db_config?raw').text)

    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()

    min = """
    SELECT MIN(similarity) FROM Recommands ORDER BY updated_time DESC LIMIT 10
    """
    cursor.execute(min)
    sim = cursor.fetchone()
    sim = list(sim)
    # print(sim[0])
    return min
get_min()