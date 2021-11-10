import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder


##### process columns set ###
def process_cols(config):
    '''
    covert column list to suitable column format for following functions
    if not isinstance(config,column) -> initialize the column to None
    '''
    if config.num_cols == '':
        num_cols = None
    else:
        num_cols = int(config.num_cols)

    try:
        columns = config.cols
        if columns == '[]' or columns == '' or columns == []:
            columns = None
        else:
            columns = columns.replace('\"','').split(',') # 들어오는 열데이터는 무조건 c1,c2,c3     형태
    except:
        columns = None
    return columns, num_cols


# string to discrete number
def str_to_int(x):
    '''
    if data-type is str, change it to discrete number
    '''
    items = np.unique(x)
    encoder = LabelEncoder()
    encoder.fit(items)

    return encoder.transform(x)

# process for decision tree data
def process_dt_data(x, y=None):
    '''
    preprocess the data for decision tree
    '''
    x = pd.DataFrame(x).dropna()

    for index, dtype in enumerate(x.dtypes):
        if dtype == bool:
            x.iloc[:, index] = x.iloc[:, index].applymap(int)
        if dtype == object:
            try:
                x.iloc[:, index] = x.iloc[:, index].astype('float')
            except:
                x.iloc[:, index] = str_to_int(x.iloc[:, index])


    if y is not None:
        y = str_to_int(y)

    return x, y

# process for decision tree data
def process_torch_data(x, y):
    '''
    preprocess the data for resnet
    '''
    x = pd.DataFrame(x).dropna()
    for index, dtype in enumerate(x.dtypes):
        if dtype == bool:
            x.iloc[:, index] = x.iloc[:, index].applymap(int)
        if dtype == object:
            try:
                x.iloc[:, index] = x.iloc[:, index].astype('float')
            except:
                x.iloc[:, index] = str_to_int(x.iloc[:, index])

    x = x.to_numpy().astype(dtype='float32')
    x = x.reshape(len(x), 1, -1)
    if y is not None:
        y = str_to_int(y)
    return x, y
