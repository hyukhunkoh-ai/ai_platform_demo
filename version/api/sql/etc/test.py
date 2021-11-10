import json
import logging
import sys
import redis

import pymysql
from version.config import redis_port, redis_ip
from version.config import db_ip, db_port, db_id, db_ps, db_name

host = db_ip
port = db_port
username = db_id  # "mct"
password = db_ps
database = db_name


try:
    conn = pymysql.connect(host=host, user=username, passwd=password, db=database, port=port, charset='utf8')
    cursor = conn.cursor()
    rd = redis.StrictRedis(host=redis_ip, port=redis_port, charset="utf-8", decode_responses=True)
except:
    logging.error("could not connect to RDS")
    sys.exit(1)


# uid = 'test1'
# select_query = "select name, cols from model_name where uid='{}'".format('test1')
# cursor.execute(select_query)
# res = cursor.fetchall()
# temp = dict()
# for (k,v) in res:
#     temp[k.strip()] = v
# temp = json.dumps(temp)
#
#
# select_query = "select distinct cols,name, type from cols_view where uid = %s"
# cursor.execute(select_query, ('test0'))
# res = cursor.fetchall()
# temp = dict()
# for k, v in enumerate(res):
#     temp[f'{k}'] = [json.loads(v[0]),v[1],v[2]]
#
# select_query = "select result from ResultLive where uid='{}'".format('test0')
# cursor.execute(select_query)
# res = cursor.fetchall()
# preds_files = []
# for i in res:
#     preds_files.append(i[0])
import pandas as pd
import io
name = 'iris.csv'
keys = rd.hvals(name)
df = pd.DataFrame(list(map(lambda x: json.loads(x), keys)))

f = io.StringIO("")
df.to_csv(f)
f.close()