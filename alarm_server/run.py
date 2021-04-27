import sys
from os import path, system

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from config import hosts

from kafka import KafkaConsumer
from json import loads

print('PROGRAM START')
import time
import boto3
import mariadb
import boto3
from botocore.config import Config

import consul

c = consul.Consul(host='54.152.246.15', port=8500)
index = None
index, data = c.kv.get('db_config', index=index)
db_config = loads(data['Value'])
conn = mariadb.connect(**db_config)
cursor = conn.cursor()

consumer = KafkaConsumer('StockInfos',
                         bootstrap_servers=[hosts.hosts.kafka_bootstrap_server_service],
                         auto_offset_reset='earlist',
                         enable_auto_commit=True,
                         group_id='my-group',
                         value_deserializer=lambda x: loads(x.decode('utf-8')),
                         )

index = None
index, data = c.kv.get('aws_config', index=index)
aws_config = loads(data['Value'])
system('mkdir ~/.aws')
access_key = aws_config['aws_access_key_id']
secret_key = aws_config['aws_secret_access_key']
echo = f'echo \'[default]\naws_access_key_id={access_key}\naws_secret_access_key={secret_key}\' > ~/.aws/credentials'
system(echo)

my_config = Config(
    region_name='us-east-1',
    signature_version='v4',
    retries={
        'max_attempts': 10,
        'mode': 'standard'
    }
)
client = boto3.client('sns', config=my_config)

search_sql = 'SELECT Users.user_id, email ' \
             'FROM Users JOIN Alarms ' \
             'WHERE Users.user_id = Alarms.user_id AND ' \
             'stock_id = ? AND ' \
             '((condition_type = 0 AND price <= ?) OR (condition_type = 1 AND price >= ?))'
get_stock_name_sql = 'SELECT stock_name ' \
                     'FROM Stocks ' \
                     'WHERE stock_id = ?'
alarm_delete_sql = 'DELETE FROM Alarms ' \
                   'WHERE user_id = ? AND stock_id = ?'
print('ITERATION START')
for message in consumer:
    value = message.value
    payload = value['payload']
    stock_id = payload['stock_id']
    trade_price = payload['trade_price']
    updated_time = payload['updated_time']
    print(f'topic : {payload}')

    cursor.execute(get_stock_name_sql, [stock_id])
    stock_name = cursor.fetchone()[0]

    cursor.execute(search_sql, [stock_id, trade_price, trade_price])
    result_set = cursor.fetchall()
    print(result_set)
    for user_id, phone_number in result_set:
        try:
            response = client.publish(
                PhoneNumber=phone_number,
                Message=f'[내일은 투자왕:{updated_time}]{stock_name} {trade_price}원입니다.',
            )
            print(f'send {updated_time}, {stock_name} to {phone_number}')
        except:
            print(f'can not send to {phone_number}')
        cursor.execute(alarm_delete_sql, [user_id, stock_id])
        conn.commit()

print('PROGRAM END')
