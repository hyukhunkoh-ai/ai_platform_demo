import argparse
import json
from version.api.sql import conn, cursor


# str_json = {'0': '<table class="engine-table" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#7134bf"> <tbody><tr><td width="100"><img src="/static/engine.png" border="0" class="decision_train" ondrop="drop(event)" ondragover="allowDrop(event)" name="train" alt="no parameters"> <b>학습엔진_tree</b> <div id="decision_train_model">Model: </div> </td></tr> </tbody></table>', '1': '<table class="engine-table" width="100%" cellpadding="0" cellspacing="0" border="0"> <tbody><tr> <td width="100"><img src="/static/engine.png" border="0" class="resnet_train" name="train" ondrop="drop(event)" ondragover="allowDrop(event)"> <b>학습엔진_resnet[ idx: 0, epoch: , lr: , bs:  ] </b> <div class="resnet_train_model">Model: </div></td></tr> </tbody></table>'}
#

def insert_engine(v, uid):

    model = json.loads(v)['name']
    texts = conn.escape_string(v)

    insert_query = "INSERT INTO EngineLive (uid,params,model) VALUES(%s, %s, %s)"
    cursor.execute(insert_query, (uid,texts,model))
    conn.commit()


def delete_engine(v,uid):
    model = json.loads(v)['name']
    texts = conn.escape_string(v)

    delete_query = "delete from EngineLive where uid = %s and params = %s and model = %s"
    cursor.execute(delete_query, (uid,texts,model))
    conn.commit()

def select_engine(uid):
    select_query = "select params,model from EngineLive where uid = %s"
    cursor.execute(select_query, (uid))
    res = cursor.fetchall()
    temp = dict()
    for k, v in enumerate(res):
        temp[f'{k}'] = v[0].replace("\\", "")
    res = json.dumps(temp)
    return res

def define_argparser():

    p = argparse.ArgumentParser()
    p.add_argument(
        '--text',
        help='json_text'
    )
    p.add_argument(
        '--uid',
        required=True,
        help='uid'
    )
    p.add_argument(
        '--type',
        help='mode'
    )
    config = p.parse_args()

    return config


if __name__ == "__main__":
    config = define_argparser()
    try:
        text = config.text
    except:
        text = None

    uid = config.uid
    mode = config.type.strip()


    if mode == "insert":
        insert_engine(text, uid)
        print('insert')
    elif mode == "delete":
        delete_engine(text,uid)
        print('delete')
    elif mode == "select":
        print(select_engine(uid))
