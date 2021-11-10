import datetime

import numpy as np
import pandas as pd
import os, pickle

from matplotlib.font_manager import FontProperties
from sklearn.tree import DecisionTreeClassifier as DTC

from version.api.parsers import Converter
from plot_utils import DT_Plot_Class
from ai_utils import Base_insert, define_argparser, Base_subprocess
from version.api.sql import conn, cursor
from ai_utils import process_dt_data, process_cols
from version.config import root_path
'''
argparse input filename, uid, mode, model_file
train
predict 
post result to train_page
'''
#####chart setting###
fontP = FontProperties()
fontP.set_size('xx-small')
##########
now = datetime.datetime.now().strftime('%y-%m-%d %H-%M')
model = 'DT'
isnn = False



class Dt_insert(Base_insert):
    def __init__(self,config, conn, cursor):
        super().__init__(config,conn,cursor)





class Supprocess_run(Base_subprocess):

    def __init__(self,config,mode='train',col_list=None,src_type='csv', num_cols=None):
        super(Supprocess_run, self).__init__(config,model,now,root_path,mode,isnn,column_list=col_list,src_type=src_type,num_cols=num_cols)
        self.name = self.model + "_" + self.uid + "_" + self.now + '.0.pkl'

    def train(self):
        x, y = process_dt_data(self.x, self.y)
        if y is None:
            raise ValueError("none y-labels")

        dtc = DTC()
        dtc.fit(x.to_numpy(), y)
        dtc.x_columns = x.columns
        dtc.y_unique = np.unique(y)
        #
        temp_path = os.path.join(root_path, 'customers', self.uid,'model', '{}'.format(self.name))
        self.temp_path = self.model_name_duplicate_check(temp_path)
        self.plot_dt(dtc)
        #

        with open(self.temp_path, "wb") as f:
            pickle.dump(dtc, f)

        ###get loss by CCE## need to define the metric which to measure the loss

        #### get accuracy##
        preds = dtc.predict(x)
        trues = y
        total_length = len(trues)
        acc_cnt = 0

        for i, j in zip(preds, trues):
            if i == j:
                acc_cnt += 1

        self.acc = np.round(acc_cnt / total_length, 3)
        self.loss = ''

        self.set_train_config()
        ###
        # config = dict(vars(config))
        ##########

        return self.config

    def retrain(self):
        pass

    def predict(self): #dataset_name,model,mdoelfile

        x, _ = process_dt_data(self.x)

        with open(self.model_path, "rb") as f:
            dtc = pickle.load(f)

        preds = dtc.predict(x)
        df = pd.DataFrame(preds).reset_index()
        df.columns = ['x_row','preds']
        converter = Converter()
        converter.df_to_redis(self.config.filename,df)
        self.set_predict_config()

        return self.config


    def plot_dt(self,dtc):
        plot_tool = DT_Plot_Class(self.name,self.uid,dtc)
        res = dict()
        chart_list = ['tree', 'feature_importance']
        for cat in chart_list:
            if cat == 'tree':
                plot_tool.tree_plot(cat)
            elif cat == 'feature_importance':
                plot_tool.fi_plot(cat)
            else:
                pass
        return res





if __name__ == '__main__':
    # np.set_printoptions(suppress=True)
    config = define_argparser()
    mode = config.mode.strip()
    src_type = config.src_type.strip()
    columns, num_cols = process_cols(config)

    run = Supprocess_run(config, mode,col_list=columns,src_type=src_type,num_cols=num_cols)

    if mode == 'train':
        train_config = run.train()
        insert = Dt_insert(train_config,conn,cursor)
        insert.train_insert()
        print(train_config.eval)
        print(train_config.train_name)# output is the model name which is use for frond-end


    elif mode == 'predict':
        predict_config = run.predict()
        insert = Dt_insert(predict_config, conn, cursor)
        insert.predict_insert()
        print(predict_config.pred_name)