import json
import os
import pandas as pd
import sys,subprocess, shutil
from version.api.parsers import Converter
from flask import *
from version.api.sql import rd
from version.api.flask import api
from version.config import root_path
from version.api.flask.flask_utils import Excel_post_utils
utils = Excel_post_utils()
converter = Converter()


## excel sheet make
@api.route('/successive_excel_sheet',methods=['GET'])
def successive_excel_sheet():
    '''
    scatter excel sheet in web
    '''
    name = request.args.get('name', None)
    type = request.args.get('type', None)

    return render_template('successive_excel.html', excel_data=name, excel_type=type)


# get initial load for excel.
@api.route('/load_big_excel', methods=['POST','GET'])
def load_big_excel():
    '''
    init the excel data in web
    '''
    if request.method == "POST":
        data = request.get_json()
        name = data['name'].strip()
        count = int(data['count'])
        data_type = data['data_type']

        uid = session.get('loginid', None)
        from_name = os.path.join(root_path, "customers", uid, "data_files", name)
        if from_name.strip()[-4:] == '.csv':
            from_name = from_name
        else:
            from_name = from_name + '.csv'


        if data_type == 'csv' or data_type == 'view_csv':

            htmls = converter.partial_from_csv_to_html(from_name, start_num=0, end_num=count)

        elif data_type == 'redis':

            htmls = converter.partial_from_redis_to_html(name,start_num=0, end_num=count)
        else:
            htmls = None
        res = dict()
        res['html'] = htmls
        res['total_len'] = converter.total_length
        return res

    return "error"

# 더보기 구현
@api.route('/load_suc_excel', methods=['POST', 'GET'])
def load_suc_excel():
    '''
    load following excel data in web when using the <- / -> button
    '''
    if request.method == "POST":
        data = request.get_json()
        name = data['name']
        start_num = data['start_num']
        end_num = data['end_num']
        data_type = data['data_type']

        uid = session.get('loginid', None)
        from_name = os.path.join(root_path, "customers", uid, "data_files", name)

        if data_type == 'csv' or data_type == 'view_csv':

            res = converter.partial_from_csv_to_html(from_name, start_num=start_num, end_num=end_num,successive=True)


        elif data_type == 'redis':

            res = converter.partial_from_redis_to_html(name, start_num=start_num, end_num=end_num,successive=True)

        else:
            res = None

        return res



# save
@api.route('/save_partial_excel', methods=['GET','POST'])
def save_partial_excel():
    '''
    save the changes in the data from web to csv
    '''
    uid = session.get('loginid',None)

    if request.method == 'POST':
        data = request.get_json()
        html = data['html']
        name = data['name'] # 확장자를 뺀 name ex) if doit.csv -> doit
        start_num = data['start_num']
        end_num = data['end_num']

        data_type = data['data_type']

        #delete keyword == html_delete
        html = utils.filter_html(html,"data-del","html_delete")
        name = os.path.join(root_path, "customers", uid, "data_files", name)

        if data_type == 'csv' or data_type == 'view_csv':
            converter.partial_from_html_to_csv(html, name, start_num=start_num, end_num=end_num)
        elif data_type == 'redis':
            converter.partial_from_html_to_csv_by_redis(html, name, start_num=start_num, end_num=end_num)

        return "sucess"

    return None

# make new excel sheet
@api.route('/save_new_excel', methods=['GET','POST'])
def save_new_excel():
    '''
    save new excel.
    '''
    uid = session.get('loginid',None)

    if request.method == 'POST':
        data = request.get_json()
        html = data['html']
        name = data['name'] # 확장자를 뺀 name ex) if doit.csv -> doit
        type = data['type']
        df = pd.read_html(html, index_col=0)[0]
        if type == 'csv' or type == 'view_csv':
            if name[-4:] == '.csv':
                save_path = os.path.join(root_path,'customers',uid,'data_files',name)
            else:
                save_path = os.path.join(root_path,'customers',uid,'data_files',name + '.csv')

            df.to_csv(save_path,index=False)
        elif type == 'redis':
            for i in range(len(df)):
                rd.hset(name, i, json.dumps(df.iloc[i,:].to_dict()))

        return "success"

    return None

# make view from csv
@api.route('/make_view', methods=['GET','POST'])
def make_view():
    '''
    make the view data and insert into DB from original CSV file
    '''
    uid = session.get('loginid',None)

    if request.method == 'POST':
        data = request.get_json()
        name = data['name']# 확장자를 뺀 name ex) if doit.csv -> doit
        ar_type = data['type']
        cols = data['cols']

        py_path = os.path.join(root_path, 'api', 'sql', 'cols_view_sql.py')

        p = subprocess.Popen(
            args=[sys.executable, py_path, '--uid', uid, '--type', ar_type, '--data_name',name, '--mode','insert','--cols',json.dumps(cols)], stdout=subprocess.PIPE)
        p.communicate()

        return "sucess"

    return None


# load html from templates
@api.route('/load_excel/<name>')
def load_excel(name):
    return render_template(name)


@api.route('/out_excel', methods=['GET','POST'])
def out_excel():
    if request.method == 'POST':
        '''
        go away
        '''

        return "sucess"

# new excel frame
@api.route('/new_excel_frame')
def new_excel_frame():
    return render_template('new_excel.html')


@api.route('/csv_copy_dedit', methods=['GET','POST'])
def csv_file_copy():
    '''
    copy the file
    '''
    uid = session.get('loginid',None)

    if request.method == 'POST':
        data = dict(request.form)
        data_name = data['data_name']# 확장자를 뺀 name ex) if doit.csv -> doit

        src_filename = data_name + '.csv'
        dst_filename = data_name + 'c.csv'
        src_file = os.path.join(root_path, 'customers', uid, 'data_files', src_filename)
        dst_file = os.path.join(root_path, 'customers', uid, 'data_files', dst_filename)
        shutil.copy(src_file, dst_file)

        return "sucess"

    return None

@api.route('/csv_delete', methods=['GET','POST'])
def csv_delete():
    uid = session.get('loginid',None)

    if request.method == 'POST':
        data = dict(request.form)
        data_name = data['data_name']# 확장자를 뺀 name ex) if doit.csv -> doit
        src_filename = data_name + '.csv'
        src_file = os.path.join(root_path, 'customers', uid, 'data_files', src_filename)
        os.remove(src_file)

        return "sucess"

    return None
