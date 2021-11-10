import argparse
import json
from version.api.sql import conn, cursor


def define_argparser():
    p = argparse.ArgumentParser()
    p.add_argument(
        '--cols',
        help='json_text'
    )
    p.add_argument(
        '--uid',
        required=True,
        help='uid'
    )
    p.add_argument(
        '--model_category',
        help='model root'
    )
    p.add_argument(
        '--data_name',
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
    if config.cols == '[]':
        setattr(config,'cols','all')
    insert_query = "INSERT INTO model_name (model_category,name,cols,uid) VALUES(%s, %s, %s, %s)"
    cursor.execute(insert_query, (config.model_category, config.data_name, config.cols,config.uid))
    conn.commit()

    return config.data_name

def select_model(config):
    select_query = "select name, cols from model_name where uid='{}'".format(config.uid)
    cursor.execute(select_query)
    res = cursor.fetchall()
    temp = dict()
    for (k, v) in res:
        select_query = "select eval from Results where user_id='{}' and model_file='{}'".format(config.uid,k.strip())
        cursor.execute(select_query)
        acc = str(round(float(cursor.fetchall()[0][0]),3)) # [['item1'],['item2']]
        temp[k.strip()] = {"col":v.replace('"',''), "acc":acc} # v = "'~'"
    temp = json.dumps(temp)
    return temp

def delete_model(config):
    # model_delete
    delete_query = "delete from model_name where uid=%s and name=%s"
    cursor.execute(delete_query,(config.uid, config.data_name))
    conn.commit()
    # model_result_delete
    delete_query = "delete from Results where user_id=%s and model_file=%s"
    cursor.execute(delete_query,(config.uid, config.data_name))
    conn.commit()


if __name__ == "__main__":
    config = define_argparser()
    if config.type == 'insert':
        print(insert_model(config))

    elif config.type == 'select':
        print(select_model(config))

    elif config.type == 'delete':
        delete_model(config)



