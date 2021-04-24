import pymysql

weather_data = [20, 10, 0, 25, 30, 1, 2, 3, 4, 5]
stock_ids = ['207940','068270','051910','035720','035420','006400','005930','005490','005380','000660']
Time = []

for i in range(5):
    Time.append("{:%Y-%m-%d-%H}-00".format(datetime.now()-timedelta(hours=i)))


url="SELECT stock_id, trade_price FROM StockInfos WHERE updated_time IN ('2021-04-19-15-58','2021-04-19-15-57','2021-04-19-15-56','2021-04-19-15-55','2021-04-19-15-54')"



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
    similarity = 0
    for idx in range(len(price_rate)):
        similarity = weather_rate[idx] - price_rate[idx]
    similarity = round(similarity, 2)
    return similarity


<<<<<<< HEAD
def insert_rec(stock_id, similarity):
    db_config = None
    with open('../config/db_config.txt', 'r') as file:
        db_config_string = file.read()
        db_config = loads(db_config_string)
=======
def insert_rec(stock_code, total):
    db_config=loads(requests.get('http://http://3.237.78.43:30500//v1/kv/db_config?raw').text)
>>>>>>> develop

    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()

 
    sql = """
    INSERT INTO Recommands (stock_id,similarity) VALUES('{}',{})
    """
    sql = sql.format(stock_id, similarity)

    cursor.execute(sql)
    conn.commit()
    print('query added')
    conn.close()



