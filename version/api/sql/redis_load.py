import argparse
import json
import os

import pandas as pd
from version.api.sql import rd, conn,cursor
from version.config import root_path

def redis_check_dataset(config):
    select_query = "select result from ResultLive where uid='{}'".format(config.uid)
    cursor.execute(select_query)
    res = cursor.fetchall()
    preds_files = []
    for i in res:
        preds_files.append(i[0])
    return preds_files

def redis_to_df(table_name):

    # all_data = rd.hgetall(table_name)
    # rows = rd.hkeys(table_name)
    values = rd.hvals(table_name)
    values = list(map(lambda x: json.loads(x),values))
    df = pd.DataFrame(values)
    return df



def redis_to_meta(config):
    res = dict()
    keys = rd.keys('*')
    preds_files = redis_check_dataset(config)
    keys = [key for key in keys if key not in preds_files]
    for k in keys:
        try:
            values = rd.hvals(k)
        except:
            continue
        cols = list(json.loads(values[0]).keys())
        res[k] = cols

    return res



def define_argparser():

    p = argparse.ArgumentParser()
    p.add_argument(
        '--uid',
        required=True,
        help='user id to be used for saving dataframe file'
    )
    p.add_argument(
        '--isredis',
        required=True,
        default=False,
        help='only redis? or to csv'
    )
    p.add_argument(
        '--filename',

        help='filename'
    )
    config = p.parse_args()

    return config



if __name__ == '__main__':

    config = define_argparser()
    if config.isredis == 'True':
        print(json.dumps(redis_to_meta(config)))

    elif config.isredis == 'False':
        uid = config.uid
        _path = os.path.join(root_path, "customers", uid, 'data_files')
        df = redis_to_df(config.filename)
        save_path = os.path.join(_path, config.filename)
        df.to_csv(save_path,index=False)
        print('success')