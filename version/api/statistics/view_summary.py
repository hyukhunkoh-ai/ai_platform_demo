import os, argparse
import json
import pandas as pd
import matplotlib.pyplot as plt
import base64
from version.api.sql import rd
from version.config import root_path
from io import BytesIO





def define_argparser():
    p = argparse.ArgumentParser()
    p.add_argument(
        '--uid',
        required=True
    )
    p.add_argument(
        '--data_name',
        required=True,
        default=None
    )
    p.add_argument(
        '--cols'
    )
    p.add_argument(
        '--data_src'
    )
    p.add_argument(
        '--data_type'
    )

    config = p.parse_args()

    return config


# cols = 'target'
# name = 'train.csv'
# # data_src = 'csv'
# data_src = 'redis'
# # data_type = 'continuous'
# data_type = 'discrete'
# uid = 'test0'

continuous_stat = ['count','mean','std','min','max']
discrete_stat = ['count','unique','top','freq']

def calculate_stat(uid,name,cols,data_src,data_type):
    '''
    input : userid, filename, data_src(csv/redis), continuous/discrete
    generate the chart depending on the model.
    '''
    statistics, df = None, None
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)
    ### data statistics
    if data_src == 'csv':
        if name[-4:] != '.csv':
            name = name + '.csv'

        data_path = os.path.join(root_path,'customers',uid,'data_files',name)
        df = pd.read_csv(data_path)

        if data_type == 'continuous':
            df = df[cols].apply(float)
            statistics = df.describe()[continuous_stat]
            ax1.plot(df)
        elif data_type == 'discrete':
            df = df[cols].apply(str)
            statistics = df.describe()[discrete_stat]
            plot_df = df.value_counts()
            plt.bar(plot_df.index,plot_df)
            plt.xlabel('labels', fontsize=18)

    elif data_src == 'redis':
        values = rd.hvals(name)
        values = list(map(lambda x: json.loads(x), values))
        df = pd.DataFrame(values)
        if data_type == 'continuous':
            df = df[cols].apply(float)
            statistics = df.describe()[continuous_stat]
            ax1.plot(df)
        elif data_type == 'discrete':
            df = df[cols].apply(str)
            statistics = df.describe()[discrete_stat]
            plot_df = df.value_counts()
            plt.bar(plot_df.index, plot_df)
            plt.xlabel('labels', fontsize=18)
            plt.ylabel('frequency', fontsize=18)



    ## chart ###
    plt.title(cols, fontsize=20)
    plt.ylabel('frequency', fontsize=18)

    buf = BytesIO()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii") # base64 bytes로 바꾸기
    img_res = f"<img src='data:image/png;base64,{data}'/>"
    df_res = statistics.to_json()
    res = df_res + '__chart__' + img_res

    return res
#


if __name__ == '__main__':
    config = define_argparser()
    res = calculate_stat(config.uid, config.data_name, config.cols, config.data_src, config.data_type)
    print(res)
