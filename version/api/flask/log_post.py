import datetime
import os
import subprocess
import sys
from flask import *

from version.api.flask import api
from version.config import root_path


########### log history ############
@api.route('/log_delete_all')
def log_delete_all():
    uid = session.get('loginid',None)

    py_path = os.path.join(root_path, 'api', 'sql', 'log_history_sql.py')
    log_p = subprocess.run(
        args=[sys.executable, py_path, '--uid', uid,'--type', 'delete'],
        capture_output=True, encoding='utf-8')
    if log_p.stderr:
        print(log_p.stderr)
        raise ValueError('sub terminal error')
    return "delete"


@api.route('/write_history/<content>')
def write_history(content):
    uid = session.get('loginid',None)
    now = datetime.datetime.now().strftime("%y-%m-%d %H-%M-%S")
    py_path = os.path.join(root_path, 'api', 'sql', 'log_history_sql.py')


    log_p_tr = subprocess.run(
        args=[sys.executable, py_path, '--uid', uid, '--log', now + " " + uid + " " + content,'--type','insert'], capture_output=True, encoding='utf-8')
    if log_p_tr.stderr:
        print(log_p_tr.stderr)
        raise ValueError('sub terminal error')
    return "written"