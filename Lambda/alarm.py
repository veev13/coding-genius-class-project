import boto3

sns = boto3.client(
"sns",
sns.publish(PhoneNumber='+821029827033', Message='안녕, AWS')

config = {
    "host": "wth-stk-svc.chik9zpsmeh8.us-east-1.rds.amazonaws.com",
    "port": 3306,
    "user": "admin",
    "password": "asdf555!",
    "database": "multicampus"
}


# db삽입
con = pymysql.connect(**config)
cur= con.cursor()

cur.execute("SELECT updated_time FROM StockInfos WHERE updated_time='{}'".format(update_Time))
exists_data = cur.fetchall()