# import json #json.loads(r.text) 제이슨파일을 딕셔너리로 바꾸기
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



