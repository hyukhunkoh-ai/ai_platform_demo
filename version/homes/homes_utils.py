import os
import shutil
from version.api.sql import rd,conn,cursor
from version.config import root_path, db_table_list

def make_directory(id):
    '''
    init the user space
    '''
    id_path = os.path.join(root_path,"customers",id)
    os.makedirs(id_path)

    with open(os.path.join(id_path,'progress.txt'),'w',encoding='utf-8') as f:
        f.write('init')

    data_path = os.path.join(id_path, "data_files")
    os.makedirs(data_path)

    model_path = os.path.join(id_path, "model")
    os.makedirs(model_path)

    res_path = os.path.join(id_path, "charts")
    os.makedirs(res_path)


def delete_directory(delete_id):
    '''
    delete user directory
    '''
    delete_path = os.path.join(root_path,"customers",delete_id)
    shutil.rmtree(delete_path)


def delete_all_db_info(delete_id):
    '''
    delete db data
    '''
    def query_gen(tablename, delete_id):
        if tablename == 'logins':
            colname = 'name'
        elif tablename == 'Results':
            colname = 'user_id'
        else:
            colname = 'uid'
        delete_query = "delete from {} where {} ='{}'".format(tablename, colname, delete_id)
        return delete_query

    for name in db_table_list:
        delete_query = query_gen(name, delete_id)
        cursor.execute(delete_query)
        conn.commit()

def delete_all_redis_info(delete_id):
    '''
    delete redis data
    '''
    keys = rd.keys(f'*_{delete_id}_*')
    for key in keys:
        rd.delete(key)


