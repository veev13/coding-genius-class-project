import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from config import hosts

from kafka import KafkaConsumer
from json import loads

import time

consumer = KafkaConsumer('StockInfos',
                         bootstrap_servers=[hosts.hosts.kafka_bootstrap_server_service],
                         auto_offset_reset='earliest',
                         enable_auto_commit=True,
                         group_id='my-group',
                         consumer_timeout_ms=1000,
                         value_deserializer=lambda x: loads(x.decode('utf-8')),
                         )

start = time.time()
for message in consumer:
    topic = message.topic
    partition = message.partition
    offset = message.offset
    key = message.key
    value = message.value
    print(message)
print('Elapsed: ', (time.time() - start))

