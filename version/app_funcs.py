import os, sys, json
import subprocess, time

class FileChangeEventCheck():
    '''
    trace whether file is changed
    '''
    def __init__(self, file_path):
        self.filename = file_path
        if os.path.isfile(self.filename):
            self._cached_stamp = os.stat(self.filename).st_mtime
        else:
            self._cached_stamp = None
    def ook(self):
        try:
            stamp = os.stat(self.filename).st_mtime
        except:
            stamp = None
        if stamp != self._cached_stamp and (self._cached_stamp is not None and stamp is not None):
            self._cached_stamp = stamp
            # something logic here
            return True
        return False

def progress_bar_generate(tpath):
    '''
    make progressbar using progress.txt until ending the train
    '''
    fev = FileChangeEventCheck(tpath)
    while 1:
        if fev.ook():
            with open(tpath, 'r') as f:
                x = f.read()
            yield "data:" + str(x).replace('\n','') + "\n\n"

        else:
            try:
                with open(tpath,'r') as f:
                    x = f.read()
                if "END__EPOCH" in x:
                    with open(tpath,'w') as f:
                        f.write('')
                    time.sleep(0.01)
                    yield "data:no" + "\n\n"
                    time.sleep(3)
                    break
            except:
                break
        time.sleep(0.1)


def get_csv_files(user_path) -> list:
    osdata_path = os.path.join(user_path, "data_files")
    if osdata_path:
        data_paths = [x[:-4] for x in os.listdir(osdata_path)]
    else:
        data_paths = []
    return data_paths


def get_model_info(root_path, loginid) -> dict:

    py_path = os.path.join(root_path, 'api', 'sql', 'ModelLive_sql.py')
    load_db_model = subprocess.run(
        args=[sys.executable, py_path, '--uid', loginid, '--type', 'select'], capture_output=True, encoding='utf-8')

    if load_db_model.stderr:
        print(load_db_model.stderr)
        raise ValueError("sub terminal error")

    model_info = json.loads(load_db_model.stdout)
    return model_info


def get_result_list(root_path, loginid) -> list:
    py_path = os.path.join(root_path, 'api', 'sql', 'ResultLive_sql.py')
    load_result = subprocess.run(
        args=[sys.executable, py_path, '--uid', loginid, '--type', 'select'], capture_output=True, encoding='utf-8')
    result_list = json.loads(load_result.stdout)

    if load_result.stderr:
        print(load_result.stderr)
        raise ValueError("sub terminal error")

    return result_list


def get_log(root_path,loginid):
    py_path = os.path.join(root_path, 'api', 'sql', 'log_history_sql.py')
    load_log_model = subprocess.run(
        args=[sys.executable, py_path, '--uid', loginid, '--type', 'select'], capture_output=True, encoding='utf-8')
    if load_log_model.stderr:
        print(load_log_model.stderr)
        raise ValueError("sub terminal error")
    logs = json.loads(load_log_model.stdout)
    return logs


def read_model_txt(root_path):
    model_list_path = os.path.join(root_path, "models.txt")
    with open(model_list_path) as f2:
        model_list = f2.read().split("\n")

    return model_list


def get_view_list(root_path, loginid):
    py_path = os.path.join(root_path, 'api', 'sql', 'cols_view_sql.py')
    load_view = subprocess.run(
        args=[sys.executable, py_path, '--uid', loginid, '--mode', 'select'], capture_output=True, encoding='utf-8')

    view_list = json.loads(load_view.stdout)
    # {'0': [['c1', 'c2', 'c3', 'target'], 'reserve', 'csv']}

    return view_list