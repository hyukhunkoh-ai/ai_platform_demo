import argparse
import json
from version.api.sql import conn, cursor,rd


def define_argparser():
    p = argparse.ArgumentParser()
    p.add_argument(
        '--filename',
        help='result'
    )
    p.add_argument(
        '--uid',
        required=True,
        help='uid'
    )
    p.add_argument(
        '--model_name',
        help='name'
    )
    p.add_argument(
        '--type',
        default='insert',
        help='mode'

    )
    config = p.parse_args()

    return config

def insert_model(config):
    insert_query = "INSERT INTO ResultLive (result,uid,model_name) VALUES(%s, %s, %s)"
    cursor.execute(insert_query, (config.filename, config.uid, config.model_name))
    conn.commit()
    return "success"

def select_model(config):
    select_query = "select result from ResultLive where uid='{}'".format(config.uid)
    cursor.execute(select_query)
    res = cursor.fetchall()
    temp = dict()
    for (k, v) in enumerate(res):
        temp[k] = v[0]
    temp = json.dumps(temp)

    return temp

def delete_model(config):
    delete_query = "delete from ai_platform.ResultLive where uid=%s and result=%s"
    cursor.execute(delete_query,(config.uid, config.filename))
    conn.commit()
    rd.delete(config.filename)
    return config.filename


if __name__ == "__main__":
    config = define_argparser()
    if config.type == 'insert':
        print(insert_model(config))

    elif config.type == 'select':
        print(select_model(config))

    elif config.type == 'delete':
        print(delete_model(config))