import os
import sys,subprocess,glob

from flask import *
from version.api.flask import api
from version.config import root_path



@api.route('/resnet_model_chart',methods=['POST'])
def resnet_model_chart():
    '''
    resnet charts handler
    '''
    uid = session.get('loginid',None)
    if request.method == 'POST':

        data = request.get_json()
        modelname = data['modelname']
        metric = data['metric']
        py_path = os.path.join(root_path, 'api', 'statistics', 'resnet_model_chart.py')

        p2 = subprocess.run(args=[sys.executable, py_path, '--uid', uid, '--modelname', modelname, '--metric', metric], capture_output=True, encoding='utf-8')
        if p2.stderr:
            print(p2.stderr)
        res = p2.stdout

        return res

    return 'fail'



@api.route('/dt_model_chart',methods=['POST'])
def dt_model_chart():
    '''
    decision tree charts handler
    '''
    uid = session.get('loginid',None)
    if request.method == 'POST':

        data = request.get_json()
        modelname = data['modelname'].strip()
        metric = data['metric'].strip()

        py_path = os.path.join(root_path, 'api', 'statistics', 'dt_model_chart.py')

        p2 = subprocess.run(args=[sys.executable, py_path, '--uid', uid, '--modelname', modelname, '--metric', metric], capture_output=True, encoding='utf-8')
        if p2.stderr:
            print(p2.stderr)
        res = p2.stdout.strip()

        return res

    return 'fail'


@api.route('/trace_html',methods=['GET'])
def trace_html():
    '''
    scatter the trace_html in web for seeing the model charts
    '''
    uid = session.get('loginid',None)
    modelname = request.args.get('modelname')
    modeltype = request.args.get('modeltype')

    return render_template('trace.html', model_name=modelname, chart_type=modeltype, uid=uid)

@api.route('/live_trained_model_delete',methods=['POST'])
def live_trained_model_delete():
    uid = session.get('loginid',None)
    if request.method == 'POST':
        data = list(request.form)[0]
        modelname = data.strip()

        py_path = os.path.join(root_path, 'api', 'sql', 'ModelLive_sql.py')

        p2 = subprocess.run(args=[sys.executable, py_path, '--uid', uid, '--data_name', modelname,'--type','delete'], capture_output=True, encoding='utf-8')

        if p2.stderr:
            print(p2.stderr)
            raise ValueError('sub terminal error')

        delete_model_path = os.path.join(root_path,'customers', uid,'model',modelname)
        os.remove(delete_model_path)

        delete_chart_path = os.path.join(root_path, 'customers', uid, 'charts', modelname)
        for chart_file in glob.glob(f'{delete_chart_path}*'):
            chart_path = os.path.join(root_path, 'customers', uid, 'charts',chart_file)
            os.remove(chart_path)

        return 'success'



    return 'fail'

@api.route('/load_chart/<filename>',methods=['GET','POST'])
def chart_directory(filename):
    '''
    load chart image from directory
    '''
    uid = session.get('loginid', None)
    directory_path = os.path.join(root_path,'customers',uid,'charts')
    return send_from_directory(directory_path, filename, as_attachment=True)

