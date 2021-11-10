import os
import sys,subprocess
from version.api.parsers import Converter
from flask import *
from version.config import root_path
from version.api.flask import api
converter = Converter()


@api.route('/view_delete', methods=['GET','POST'])
def view_delete():
    uid = session.get('loginid',None)

    if request.method == 'POST':
        data = dict(request.form)
        name = data['name']
        cols = data['cols']
        py_path = os.path.join(root_path, 'api', 'sql', 'cols_view_sql.py')

        p = subprocess.run(
            args=[sys.executable, py_path, '--uid', uid, '--data_name',name,'--mode','delete','--cols', cols], capture_output=True, encoding='utf-8')

        if p.stderr:
            print(p.stderr)
            raise ValueError('sub terminal error')

        return "success"

    return None



@api.route('/view_sheet',methods=['GET'])
def view_sheet():
    name = request.args.get('name', None)
    cols = request.args.get('cols', None).split(',')
    data_type = request.args.get('type', None)

    return render_template('view.html', excel_data=name,column_data=cols, excel_type=data_type)




@api.route('/fragment_view', methods=['POST','GET'])
def fragment_view():
    '''
    scatter the sample data to see what data type is in view.html
    '''
    uid = session.get('loginid', None)
    if request.method == "POST":
        data = request.get_json()
        name = data['name'].strip()
        count = int(data['count'])
        cols = data['cols'].strip('\"').split(',') # ['1','2','3'] string to list
        data_type = data['data_type']

        from_name = os.path.join(root_path, "customers", uid, "data_files", name)


        if from_name.strip()[-4:] == '.csv':
            from_name = from_name
        else:
            from_name = from_name + '.csv'


        if data_type == 'csv' or data_type == 'view_csv':
            res = converter.partial_from_csv_to_html(from_name, start_num=0, end_num=count,extract_cols=cols)
        elif data_type == 'redis':
            res = converter.partial_from_redis_to_html(name, start_num=0, end_num=count,extract_cols=cols)
        else:
            res = None

        return res

    return "error"

@api.route('/get_summary_of_column',methods=['POST'])
def get_summary_of_column():
    '''
    calculate the column data's statistics and get the regression/histogram chart in a bytes format
    '''
    uid = session.get('loginid', None)
    if request.method == 'POST':
        data = request.get_json()
        name = data['name']
        cols = data['colname']

        data_src = data['data_src']
        data_type = data['data_type']
        py_path = os.path.join(root_path, 'api', 'statistics', 'view_summary.py')

        p2 = subprocess.run(args=[sys.executable, py_path, '--uid',uid,'--data_name',name,'--cols',cols,'--data_src',data_src,'--data_type',data_type],capture_output=True, encoding='utf-8')

        if p2.stderr:
            print(p2.stderr)

        return p2.stdout

    return "fail"