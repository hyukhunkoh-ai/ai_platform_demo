import os,time
import pandas as pd
from io import StringIO
from version.api.sql import rd
from pathlib import Path
from flask import *
from config import root_path

downloads = Blueprint('downloads', __name__)

@downloads.route('/model/downloader', methods = ['GET', 'POST'])
def model_downloader():
    name = ''
    if request.method == 'POST':
        name = request.form.get('filename')
        print(name)
    return send_file("model/{}".format(name), as_attachment=True)


@downloads.route('/data_downloads/<filename>',methods=['GET'])
def data_downloads(filename):
    uid = session.get('loginid')
    if request.method == 'GET':
        filename = filename
        filepath = os.path.join(root_path, 'customers', uid, 'data_files')
        ispath = os.path.join(root_path, 'customers', uid, 'data_files', filename)
        while 1:
            time.sleep(2)
            file_directory = Path(ispath)
            if file_directory.is_file():
                break

    return send_from_directory(directory=filepath, filename=filename)


@downloads.route('/redis_data_downloads/<filename>',methods=['GET'])
def redis_data_downloads(filename):
        ## dataframe을 저장할 IO stream
        output_stream = StringIO()
        keys = rd.hvals(filename)
        df = pd.DataFrame(list(map(lambda x: json.loads(x), keys)))

        ## 그 결과를 앞서 만든 IO stream에 저장해줍니다.
        df.to_csv(output_stream, index=False)
        response = Response(
            output_stream.getvalue(),
            mimetype='text/csv',
            content_type='application/octet-stream',
        )

        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        return response


@downloads.route('/model_downloads/<filename>',methods=['GET'])
def model_downloads(filename):
    uid = session.get('loginid')
    if request.method == 'GET':
        filename = filename
        filepath = os.path.join(root_path, 'customers', uid, 'model')
        ispath = os.path.join(root_path, 'customers', uid, 'model', filename)
        while 1:
            time.sleep(2)
            file_directory = Path(ispath)
            if file_directory.is_file():
                break

    return send_from_directory(directory=filepath, filename=filename)


@downloads.route('/downloads/<filename>', methods=['GET'])
def private_downloads(filename):
    uid = session.get('loginid')

    if request.method == 'GET':
        filename = filename
        filepath = os.path.join(root_path, 'customers', uid, 'result')
        ispath = os.path.join(root_path, 'customers', uid, 'result',filename)
        while 1:
            time.sleep(2)
            file_directory = Path(ispath)
            if file_directory.is_file():
                break

    return send_from_directory(directory=filepath, filename=filename)