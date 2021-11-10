import redis
import csv
import json
rd = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
table_name = 'reserve.csv'
with open(table_name, 'r') as f:
    t = csv.reader(f)
    num = 0
    idx_hash = []
    values = []
    for idx,r in enumerate(t):
        if num == 0:
            # r[0] => index라고 가정
            cols = r
            num = -1
        else:
            temp_dict = dict()
            idx_hash.append(idx)
            for idx, v in enumerate(r):
                temp_dict[cols[idx]] = v
            values.append(temp_dict)

assert len(idx_hash) == len(values)
for i,j in zip(idx_hash, values):
    rd.hset('iris.csv',i,json.dumps(j))