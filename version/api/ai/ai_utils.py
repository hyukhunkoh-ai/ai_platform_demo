from preprocessing import process_cols,str_to_int ,process_dt_data, process_torch_data
import argparse
import datetime
import os
import abc
import numpy as np
import pandas as pd
from version.api.parsers import Converter

coverter = Converter()



class Base_insert(abc.ABC):
    '''
    inherit and init the hyper parameters and loss only
    '''
    @abc.abstractmethod
    def __init__(self, config, conn, cursor):
        '''
        initialize the self.hyper_parameter & self.loss
        '''
        self.config = config
        self.conn = conn
        self.cursor = cursor
        self.hyper_parameter = None
        self.loss = None

    def train_insert(self):
        '''
        input :
        # json_str = "{'data_file': 'test-label.csv', 'mode': 'predict', 'model_file': 'DT_test1_21-02-04 17-17.pkl', 'name': 'preds_by_DT_test1_21-02-04 17-17.pkl_time_21-02-05 11-49', 'uid': 'test1'}"
        {'data_file': 'datafile', 'uid': 'test1', 'mode': 'train', 'epochs': epoch, 'lr': lr, 'bs': bs,
         'model_file': '', 'loss': loss, 'eval': eval,}
         '''
        now = datetime.datetime.now().strftime('%y-%m-%d %H-%M')
        insert_query = "INSERT INTO Results (user_id, stat_dt, end_dt, hyper_parameter, model_file, input, pred, eval, loss) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"



        user_id = self.config.uid
        stat_dt = self.config.train_name.split('_')[-1].split('.')[0]
        end_dt = now
        hyper_parameter = self.hyper_parameter
        # hyper_parameter = str({'epcohs': self.config.epochs, 'lr': self.config.lr, 'bs': self.config.bs})
        model_file = self.config.train_name
        input_ = self.config.data_file
        pred = None
        eval = self.config.eval
        loss = self.loss
        # loss = self.config.loss

        values = (user_id, stat_dt, end_dt, hyper_parameter, model_file, input_, pred, eval, loss)

        self.cursor.execute(insert_query, values)
        self.conn.commit()

        query = "SELECT no from Results WHERE user_id = '{}' and input = '{}'".format(user_id, input_)
        self.cursor.execute(query)

        res_no = self.cursor.fetchall()
        no_list = []  # id number list
        for i in res_no:
            no_list.append(list(i)[0])

        return no_list

    def retrain_insert(self):
        '''
        input :
        # json_str = "{'data_file': 'test-label.csv', 'mode': 'predict', 'model_file': 'DT_test1_21-02-04 17-17.pkl', 'name': 'preds_by_DT_test1_21-02-04 17-17.pkl_time_21-02-05 11-49', 'uid': 'test1'}"
        {'data_file': 'datafile', 'uid': 'test1', 'mode': 'train', 'epochs': epoch, 'lr': lr, 'bs': bs,
         'model_file': '', 'loss': loss, 'eval': eval,}
         '''

        now = datetime.datetime.now().strftime('%y-%m-%d %H-%M')
        insert_query = "INSERT INTO Results (user_id, stat_dt, end_dt, hyper_parameter, model_file, input, pred, eval, loss) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"

        user_id = self.config.uid
        stat_dt = self.config.retrain_name.split('_')[-1].split('.')[0]
        end_dt = now
        hyper_parameter = self.hyper_parameter
        # hyper_parameter = str({'epcohs': self.config.epochs, 'lr': self.config.lr, 'bs': self.config.bs})
        model_file = self.config.retrain_name
        input_ = self.config.data_file
        pred = None
        eval = self.config.eval
        loss = self.loss
        # loss = self.config.loss

        values = (user_id, stat_dt, end_dt, hyper_parameter, model_file, input_, pred, eval, loss)

        self.cursor.execute(insert_query, values)
        self.conn.commit()

        query = "SELECT no from Results WHERE user_id = '{}' and input = '{}'".format(user_id, input_)
        self.cursor.execute(query)

        res_no = self.cursor.fetchall()
        no_list = []  # id number list
        for i in res_no:
            no_list.append(list(i)[0])

        return no_list

    def predict_insert(self):
        '''
        input :
        {'data_file': 'datafile', 'uid': 'test1', 'mode': 'train', 'epochs': epoch, 'lr': lr, 'bs': bs,
                 'model_file': '', 'loss': loss, 'eval': eval,
                 'train_name': model name}
        '''
        now = datetime.datetime.now().strftime('%y-%m-%d %H-%M')



        user_id = self.config.uid
        pred_name = self.config.pred_name
        end_dt = now
        model_file = self.config.model_file

        query = "UPDATE Results SET pred=%s, end_dt=%s WHERE model_file=%s"
        values = (pred_name, end_dt, model_file)
        self.cursor.execute(query, values)
        self.conn.commit()

        query = "SELECT no from Results WHERE user_id = '{}' and pred = '{}'".format(user_id, pred_name)
        self.cursor.execute(query)
        res_no = self.cursor.fetchall()
        no_list = []
        for i in res_no:
            no_list.append(list(i)[0])
        # 자료 아이디값
        return no_list

    def __str__(self):
        res = f'{self.__class__.__name__}'
        return f"{res} is BASE INSERT MODULE for saving train/predict result in the DB"

    def __getattr__(self, item):
        return getattr(self.config, item)



class Base_subprocess(abc.ABC):
    '''
    when u inherit then init, just make the name and assign to self.name
    '''
    def __init__(self, config, modelname, now, root_path, mode='train', neural_net=True, column_list=None, src_type='csv',num_cols=None):
        self.config = config
        self.model = modelname
        self.new_name = None
        self.now = now
        self.root_path = root_path
        self.column_list = column_list
        self.name = None

        self.loss = None
        self.acc = None
        self.name = None

        if neural_net:
            self.nn_init(config)

        self.uid = config.uid
        self.data = config.data_file # dataset name or table name

        ######## load data
        data_path = os.path.join(self.root_path, "customers", self.uid, 'data_files', self.data)
        self.get_data_src(src_type,data_path)
        self.x, self.y = self.data_split_with_extracted_cols(column_list)
        ####################



        if mode == 'retrain':
            self.model_path = os.path.join(self.root_path, "customers", self.uid, 'model', config.model_file)
            if 'retrain' in config.model_file:
                self.new_name = self.config.model_file + '.0.pt'
            else:
                self.new_name = self.model + '_retrain0' + "_by-" + self.config.model_file + '.0.pt'

        elif mode == 'predict':
            self.model_path = os.path.join(self.root_path, "customers", self.uid, 'model', config.model_file)


        if num_cols == None or num_cols == '' or num_cols == '[]':
            self.num_cols = len(self.x.columns)
        else:
            self.num_cols = num_cols


    def __str__(self):
        res = f'{self.__class__.__name__}'
        return f"{res} is Subprocess_BASE module : it is for model train/predict handler module."

    def __getattr__(self, item):
        return getattr(self.config,item)

    def get_data_src(self,dtype,data_path):
        '''
        load and generate self.data
        input : data_type, data_path
        '''
        if dtype == 'csv' or dtype == 'view_csv':
            if self.data[-4:] == '.csv':
                self.data = pd.read_csv(data_path, header=0)
            else:
                self.data = pd.read_csv(data_path + '.csv', header=0)
        elif dtype == 'redis':
            self.data = coverter.redis_to_df(self.data)

    def data_split_with_extracted_cols(self,cols):
        '''
        split data into x & y
        input : target columns
        output : x,y
        '''
        if cols:
            x = self.data[cols]
            x = x[x.columns.difference(['label', 'target'])]
        else:
            x = self.data[self.data.columns.difference(['label', 'target'])]

        y = None

        if 'target' in self.data.columns:
            y = self.data['target']
            self.num_outputs = len(y.unique())
        elif 'label' in self.data.columns:
            y = self.data['label']
            self.num_outputs = len(y.unique())

        return x,y

    def nn_init(self,config):
        '''
        initialize only for DNN
        input : config
        content : lr,epochs,bs
        '''
        self.lr = np.float32(config.lr)
        self.epochs = int(config.epochs)
        self.bs = int(config.bs)


    def set_train_config(self):
        setattr(self.config, 'loss', self.loss)
        setattr(self.config, 'eval', self.acc)
        setattr(self.config, 'train_name', self.name)

    def set_retrain_config(self):
        setattr(self.config, 'loss', self.loss)
        setattr(self.config, 'eval', self.acc)
        setattr(self.config, 'retrain_name', self.new_name)

    def set_predict_config(self):
        setattr(self.config, 'pred_name', self.config.filename)  # set filename

    def model_name_duplicate_check(self,path,retrain=False):
        '''
        model filename duplicate check
        '''
        while (1):
            if os.path.isfile(path):
                temp_edit_path = path.split('.')
                temp_index = int(temp_edit_path[-2]) + 1
                temp_edit_path[-2] = str(temp_index)
                path = ".".join(temp_edit_path)
                if retrain:
                    temp_edit_name = self.new_name.split('.')
                    temp_edit_name[-2] = str(temp_index)
                    self.new_name = ".".join(temp_edit_name)
                else:
                    temp_edit_name = self.name.split('.')
                    temp_edit_name[-2] = str(temp_index)
                    self.name = ".".join(temp_edit_name)

            if not os.path.isfile(path):
                break

        return path

    def model_retrain_times_check(self,path):
        '''
        trace the number of retrain and reflect into the model filename
        '''
        filename = self.config.model_file

        if 'retrain' in filename.split('_')[1]:
            temp = self.new_name.split('_', 2)
            replaced_idx = int(temp[1][-1]) + 1
            replaced_string = 'retrain' + str(replaced_idx)
            temp[1] = replaced_string
            self.new_name = "_".join(temp)

        res = path.split(os.path.sep)
        res[-1] = self.new_name
        res = "/".join(res)
        return res

    @abc.abstractmethod
    def train(self):
        '''
        {'data_file': 'datafile', 'uid': 'test1', 'mode': 'train', 'epochs': epoch, 'lr': lr, 'bs': bs,
         'model_file': '', 'loss': loss, 'eval': eval,
         'train_name': model name}
        '''
        return self.config

    # #
    @abc.abstractmethod
    def retrain(self):
        '''
        {'data_file': 'datafile', 'uid': 'test1', 'mode': 'train', 'epochs': epoch, 'lr': lr, 'bs': bs,
           'model_file': '', 'loss': loss, 'eval': eval,
           'train_name': model name}
        '''
        return self.config

    @abc.abstractmethod
    def predict(self):

        return self.config




# --name 쓰면 작동 안함
def define_argparser():
    #{'data_file': datafile, 'uid',:userid, 'mode':'train','
    p = argparse.ArgumentParser()
    p.add_argument(
        '--data_file',

        help='data file name to continue.'
    )
    p.add_argument(
        '--uid',
        required=True,
        help='being used to make model file name'
    )
    p.add_argument(
        '--mode',
        default='train',
        help='chose train or predict or retrain'
    )
    p.add_argument(
        '--epochs',
        default=50,
        help='how much train'
    )
    p.add_argument(
        '--lr',
        default=0.001,
        help='learning rate'
    )
    p.add_argument(
        '--bs',
        default=16,
        help='batch_size'
    )
    p.add_argument(
        '--model_file',
        default='',
        help='upload model file and use for predict or retrain '
    )
    p.add_argument(
        '--loss',
        default='',
        help='for loss'
    )
    p.add_argument(
        '--eval',
        default='',
        help='for accuracy'
    )
    p.add_argument(
        '--filename',
        default='',
        help='for save'
    )
    p.add_argument(
        '--num_cols',
        default='',
        help='the number of columns, default is iris dataset',
    )
    p.add_argument(
        '--cols',
        default='',
        help='what columns to be used',
    )

    p.add_argument(
        '--src_type',
        default='csv',
        help='data from redis?',
    )


    config = p.parse_args()

    return config






