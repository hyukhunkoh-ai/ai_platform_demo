import datetime
import json
import os
import subprocess
import sys

from flask import *

from version.api.flask import api

from version.config import root_path
from version.api.flask.flask_utils import Ai_post_utils
utils = Ai_post_utils()

@api.route('/train_page',methods =['POST','GET'])
def train_page():
    '''
    get data from api.html
    Then execute model train and save the result in Result DB
    Afterwards insert the generated model into modellive DB
    '''
    uid = session.get('loginid')
    if request.method == 'POST':
        data = request.get_json()
        dataset = data['dataset'] # dataset_이름에서 이름만
        model = data['model'] # model_이름에서 이름만
        column_list = data['columns']
        num_cols = utils.make_num_cols(column_list)
        src_type = data['src_type']

        if model == 'decision': #filename, uid

            py_path = os.path.join(root_path, 'api', 'ai', 'decision_tree.py')

            pdt = subprocess.run(args=[sys.executable, py_path, '--data_file', dataset, '--uid', uid,'--cols', json.dumps(column_list),'--src_type',src_type], capture_output=True, encoding='utf-8')
            pdt_res = pdt.stdout.split('\n')

            t_acc = pdt_res[0]
            data_name = pdt_res[1]

            if pdt.stderr:
                print(pdt.stderr)
                raise ValueError("sub terminal error")

            py_path2 = os.path.join(root_path, 'api', 'sql', 'ModelLive_sql.py')
            db_pdt = subprocess.run(args=[sys.executable, py_path2, '--model_category', 'tree', '--uid', uid,'--cols', json.dumps(column_list),'--data_name', data_name], capture_output=True, encoding='utf-8')
            filename = db_pdt.stdout.strip()
            if filename == '':
                print(db_pdt.stderr)
                raise ValueError("sub terminal error")

            res = {'acc':str(t_acc), 'filename':filename.strip()}

            return json.dumps(res)



        elif model == 'resnet':

            hyper_params = data['hyper_params']
            ep,lr,bs = utils.hyper_parmas_spliter(hyper_params)

            py_path = os.path.join(root_path, 'api', 'ai', 'torch_resnet.py')



            prn = subprocess.run(args=[sys.executable, py_path, '--data_file', dataset, '--uid', uid, '--epochs', ep, '--lr', lr, '--bs', bs, '--cols', json.dumps(column_list),'--src_type',src_type,'--num_cols',str(num_cols)], capture_output=True,encoding='utf-8')
            prn_res = prn.stdout.split('\n')
            t_acc = prn_res[0]
            data_name = prn_res[1]

            if prn_res == '':
                print(prn.stderr)
                raise ValueError("sub terminal error")

            py_path2 = os.path.join(root_path, 'api', 'sql', 'ModelLive_sql.py')
            db_prn = subprocess.run(args=[sys.executable, py_path2, '--model_category', 'cnn', '--uid', uid,'--cols', json.dumps(column_list),'--data_name', data_name], capture_output=True, encoding='utf-8')
            filename = db_prn.stdout
            if filename == '':
                print(db_prn.stderr)
                raise ValueError("sub terminal error")



            '''{'data_file': 'datafile', 'uid': 'test1', 'mode': 'train', 'epochs': epoch, 'lr': lr, 'bs': bs,
             'model_file': '', 'loss': loss, 'eval': eval,
             'train_name': model name}'''

            res = {'acc': round(float(t_acc),3), 'filename':filename.strip()}

            return json.dumps(res)



    return "no api has been made"

@api.route('/retrain_page',methods =['POST','GET'])
def retrain_page():
    '''
    get data from api.html
    Then execute model retrain and save the result in Result DB
    Afterwards insert the generated model into modellive DB
    '''
    uid = session.get('loginid')
    if request.method == 'POST':

        data = request.get_json() # {"dataset": data_name,"model" : model_name,"mode":mode}
        dataset = data['dataset'] # dataset_이름에서 이름만
        model = data['model'] # [model_이름]에서 모델만, decision, if문 들어갈 판별용
        model_file = data['model_file']#모델 파일 이름
        column_list = data['columns']
        src_type = data['src_type']


        if model == 'resnet':
            hyper_params = data['hyper_params']
            ep,lr,bs = utils.hyper_parmas_spliter(hyper_params)

            py_path = os.path.join(root_path, 'api', 'ai', 'torch_resnet.py')


            prrn = subprocess.run(args=[sys.executable, py_path, '--data_file', dataset,'--mode', 'retrain', '--model_file',model_file, '--uid', uid, '--epochs', ep, '--lr', lr, '--bs', bs,'--src_type',src_type,'--cols', json.dumps(column_list)], capture_output=True,encoding='utf-8')

            prrn_res = prrn.stdout.split('\n')
            t_acc = prrn_res[0]
            data_name = prrn_res[1]
            if prrn_res == '':
                print(prrn.stderr)
                raise ValueError("sub terminal error")
            py_path2 = os.path.join(root_path, 'api', 'sql', 'ModelLive_sql.py')
            db_prrn = subprocess.run(args=[sys.executable, py_path2, '--model_category', 'cnn', '--uid', uid, '--cols', json.dumps(column_list), '--data_name',data_name], capture_output=True, encoding='utf-8')
            filename = db_prrn.stdout
            if filename == '':
                print(db_prrn.stderr)
                raise ValueError("sub terminal error")


            res = {'acc':round(float(t_acc),3),'filename':filename.strip()}

            return json.dumps(res)



    return "fail"


@api.route('/predict_page',methods =['POST','GET'])
def predict_page():
    '''
    get data from api.html
    Then execute model predict and update the result in Result DB
    Afterwards insert the generated model into resultlive DB
    '''
    uid = session.get('loginid')

    if request.method == 'POST':
        data = request.get_json()
        dataset = data['dataset'] # [dataset_이름]에서 이름만
        model = data['model'] # [model_이름]에서 모델만, decision, if문 들어갈 판별용
        model_file = data['model_file']#모델 파일 이름
        src_type = data['src_type']
        column_list = data['columns']


        if model == 'decision':  # dataset, filename
            py_path1 = os.path.join(root_path, 'api', 'ai', 'decision_tree.py')

            now = datetime.datetime.now().strftime('%y-%m-%d %H-%M')
            filename = f'{src_type}_{dataset}_preds_by_' + model_file + '_time_' + now
            p1 = subprocess.run(
                args=[sys.executable, py_path1, '--data_file', dataset, '--uid', uid, '--mode', 'predict', '--model_file', model_file, '--filename', filename,'--src_type',src_type,'--cols', json.dumps(column_list)],capture_output=True, encoding='utf-8')
            if p1.stderr:
                print(p1.stderr)
                raise ValueError("sub terminal error")

            py_path2 = os.path.join(root_path, 'api', 'sql', 'ResultLive_sql.py')

            p2 = subprocess.run(
                args=[sys.executable, py_path2,'--uid', uid, '--mode', 'insert','--filename', filename, '--model_name', model_file], capture_output=True,encoding='utf-8')

            if p2.stderr:
                print(p2.stderr)
                raise ValueError("sub terminal error")

            return filename



        elif model == 'resnet':
            # model_path = os.path.join(root_path, "customers", uid, 'model', 'DT_test1_21-02-04 17-17.pkl')

            py_path2 = os.path.join(root_path, 'api', 'ai', 'torch_resnet.py')
            now = datetime.datetime.now().strftime('%y-%m-%d %H-%M')
            filename = f'{src_type}_{dataset}_preds_by_' + model_file + '_time_' + now

            p3 = subprocess.run(
                args=[sys.executable, py_path2, '--data_file', dataset, '--uid', uid, '--mode', 'predict', '--model_file', model_file, '--filename', filename,'--src_type',src_type,'--cols', json.dumps(column_list)], encoding='utf-8',check=True) #,capture_output=True , check=true하면 stderr로 안 들어감
            if p3.stderr:
                print(p3.stderr)
                raise ValueError("sub terminal error")

            py_path2 = os.path.join(root_path, 'api', 'sql', 'ResultLive_sql.py')
            p4 = subprocess.run(
                args=[sys.executable, py_path2, '--uid', uid, '--mode', 'insert', '--filename', filename,'--model_name', model_file], capture_output=True, encoding='utf-8')
            if p4.stderr:
                print(p4.stderr)
                raise ValueError("sub terminal error")


            return filename

    return "no api"



