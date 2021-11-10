import json
import os
import pandas as pd
import sys,subprocess

from io import StringIO
from flask import *
from version.api.flask import api
from version.api.sql import rd
from version.config import root_path
# 변하지 않는 파일이라면,send_file이 좋고, 임시로 만들어지는 파일이라면, Response가 good



@api.route('/live_result_delete',methods=['POST'])
def live_result_delete():
    if request.method == 'POST':
        loginid = session.get('loginid', None)
        data = list(request.form)[0].strip('\"')

        py_path = os.path.join(root_path, 'api', 'sql', 'ResultLive_sql.py')
        py_path2 = os.path.join(root_path, 'api', 'sql', 'ResultLive_rd.py')

        p = subprocess.run(
            args=[sys.executable, py_path,'--filename', data, '--uid', loginid,'--type', 'delete'], capture_output=True, encoding='utf-8')
        if p.stderr:
            print(p.stderr)
            raise ValueError("sub terminal error")
        p2 = subprocess.run(
            args=[sys.executable, py_path2, '--filename', data, '--type', 'delete'],
            capture_output=True, encoding='utf-8')
        if p2.stderr:
            print(p.stderr)
            raise ValueError("sub terminal error")



        return "success"

    return "error"

@api.route('/result_download_from_redis/<result_name>')
def result_download_from_redis(result_name):
    '''
    Make response with redis data and
    send the response which is our prediction made by model in a file format to user
    '''
    ## dataframe을 저장할 IO stream
    output_stream = StringIO()
    keys = rd.hvals(result_name)
    df = pd.DataFrame(list(map(lambda x: json.loads(x), keys)))

    ## 그 결과를 앞서 만든 IO stream에 저장해줍니다.
    df.to_csv(output_stream,index=False)
    response = Response(
        output_stream.getvalue(),
        mimetype='text/csv',
        content_type='application/octet-stream',
    )

    response.headers["Content-Disposition"] = f"attachment; filename={result_name}"

    return response
