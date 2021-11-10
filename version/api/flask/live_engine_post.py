import json
import subprocess, sys
import os
from flask import request, session
from version.api.flask import api
from version.config import root_path


@api.route('/live_engine_insert', methods=['POST'])
def live_engine_insert():
    if request.method == 'POST':
        loginid = session.get('loginid',None)
        data = json.dumps(request.form)

        py_path = os.path.join(root_path, 'api', 'sql', 'EngineLive_sql.py')
        p1 = subprocess.run(
            args=[sys.executable, py_path, '--text', data,'--uid',loginid,'--type','insert'], capture_output=True, encoding='utf-8')

        if p1 == '':
            print(p1.stderr)
            raise ValueError("sub terminal error")

        return "success"

@api.route('/live_engine_load', methods=['POST'])
def live_engine_load():
    if request.method == 'POST':
        loginid = session.get('loginid', None)

        py_path = os.path.join(root_path, 'api', 'sql', 'EngineLive_sql.py')
        p3 = subprocess.run(
            args=[sys.executable, py_path,'--uid', loginid,'--type', 'select'], capture_output=True, encoding='utf-8')
        res = json.loads(p3.stdout)

        if p3 == '':
            print(p3.stderr)
            raise ValueError("sub terminal error")

        return res

@api.route('/live_engine_delete',methods=['POST'])
def live_engine_delete():
    if request.method == 'POST':
        loginid = session.get('loginid', None)
        data = json.dumps(dict(request.form))

        py_path = os.path.join(root_path, 'api', 'sql', 'EngineLive_sql.py')

        p3 = subprocess.run(
            args=[sys.executable, py_path,'--text', data, '--uid', loginid,'--type', 'delete'], capture_output=True, encoding='utf-8')

        if p3 == '':
            print(p3.stderr)
            raise ValueError("sub terminal error")
        return "success"

    return "error"