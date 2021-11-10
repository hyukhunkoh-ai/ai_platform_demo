'''
it is for view table from the original csv with selected columns
'''


import argparse
import json
from version.api.sql import conn, cursor


def insert_view(uid,name,type,cols):

    if not cols == '[]':
        insert_query = "INSERT INTO cols_view (uid,name,type,cols) VALUES(%s, %s, %s, %s)"
        cursor.execute(insert_query, (uid,name,type,cols))
        conn.commit()


def delete_view(uid,name,cols):

    delete_query = "delete from cols_view where uid = %s and name = %s and cols = %s"
    cursor.execute(delete_query, (uid,name,cols))
    conn.commit()

def select_view(uid):
    select_query = "select distinct cols,name, type from cols_view where uid = %s"
    cursor.execute(select_query, (uid))
    res = cursor.fetchall()
    temp = dict()
    for k, v in enumerate(res):
        temp[f'{k}'] = [json.loads(v[0]),v[1],v[2]]
    res = json.dumps(temp)
    return res

def define_argparser():

    p = argparse.ArgumentParser()

    p.add_argument(
        '--cols',
        help='json_text'
    )
    p.add_argument(
        '--data_name',

        help='name'
    )
    p.add_argument(
        '--uid',
        required=True,
        help='uid'
    )

    p.add_argument(
        '--type',
        help='redis, csv'
    )

    p.add_argument(
        '--mode',
        help='mode'
    )



    res = p.parse_args()

    return res




if __name__ == "__main__":
    config = define_argparser()
    uid = config.uid
    mode = config.mode.strip()

    try:
        ar_type = config.type.strip()
    except:
        ar_type = None
    try:
        name = config.data_name.strip()
    except:
        name = None
    try:
        cols = config.cols.strip()
    except:
        cols = None




    if mode == "insert":
        insert_view(uid,name,ar_type,cols)
        print(name)
    elif mode == "delete":
        cols = str(cols.split(',')).replace("\'","\"")
        delete_view(uid,name,cols)
        print(cols)
    elif mode == "select":
        print(select_view(uid))
