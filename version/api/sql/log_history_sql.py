import argparse
import json
from version.api.sql import conn, cursor





def define_argparser():
    p = argparse.ArgumentParser()
    p.add_argument(
        '--uid',
        required=True,
        help='uid'
    )
    p.add_argument(
        '--log',
        help='text'
    )
    p.add_argument(
        '--type',
        help='mode'
    )
    config = p.parse_args()

    return config

def insert_log(config):

    insert_query = "INSERT INTO log_history (uid,log) VALUES(%s, %s)"
    log = conn.escape_string(config.log)
    cursor.execute(insert_query, (config.uid, log))
    conn.commit()
    return "success"

def select_log(config):
    select_query = "select log from log_history where uid='{}'".format(config.uid)
    cursor.execute(select_query)
    res = cursor.fetchall()
    temp = dict()

    for (k, v) in enumerate(res):

        temp[k] = v[0].strip()
    temp = json.dumps(temp)

    return temp


def delete_log(config):
    delete_query = "delete from log_history where uid='{}'".format(config.uid)
    cursor.execute(delete_query)
    conn.commit()
    return 'success'

if __name__ == "__main__":
    config = define_argparser()
    if config.type == 'insert':
        # print(insert_log(config))
        insert_log(config)
    elif config.type == 'select':
        print(select_log(config))
    elif config.type == 'delete':
        print(delete_log(config))