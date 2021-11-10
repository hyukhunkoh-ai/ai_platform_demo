import os
import sys,subprocess
from flask import *

from version.api.flask import api
from version.config import root_path



@api.route('/redis_load',methods=['POST'])
def redis_load():
    if request.method == 'POST':

        uid = session.get('loginid', None)

        py_path = os.path.join(root_path, 'api', 'sql', 'redis_load.py')

        p = subprocess.run(
            args=[sys.executable, py_path,'--uid', uid,'--isredis','True'], capture_output=True, encoding='utf-8')

        if p.stderr:
            print(p.stderr)
            raise ValueError("sub terminal error")
        # table_name : columns
        return p.stdout

    return "error"
