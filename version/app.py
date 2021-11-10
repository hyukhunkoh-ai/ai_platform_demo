import os
from werkzeug.utils import secure_filename
from functools import partial
from app_funcs import get_csv_files,get_model_info,get_result_list,get_log,read_model_txt,get_view_list
from app_funcs import progress_bar_generate

from flask import *
from flask import Flask
from flask_wtf.csrf import CSRFProtect

from version.api.flask import api
from app_downloader import downloads
from config import host_addr, port_num, root_path
from forms import aiform, dtform
from homes import homes


app = Flask(__name__)
app.register_blueprint(api)  #url_prefix='/api'
app.register_blueprint(homes)
app.register_blueprint(downloads)



@app.route('/api',methods=['GET','POST'])
def api():
    '''
    init the api.html
    '''
    loginid = session.get('loginid',None)
    user_path = os.path.join(root_path, "customers", loginid)

    ###########
    csv_data_list = get_csv_files(user_path)
    model_info = get_model_info(root_path,loginid)
    result_list = get_result_list(root_path,loginid)
    logs = get_log(root_path,loginid)
    model_list = read_model_txt(root_path)
    view_list = get_view_list(root_path,loginid)
    ############


    ###forms-- related to engine add ####
    ai_form = aiform()
    dt_form = dtform()


    if not loginid:
        return "로그인하고 들어와요. ex 혁훈이짱1"
    return render_template('api.html', loginid=loginid, rpath=result_list,csv_data_list=csv_data_list, mpath=model_info,logs=logs, mlist=model_list[:-1], vlist=view_list, aiform=ai_form, dtform=dt_form)


@app.route('/datafile_upload', methods=['GET','POST'])
def datafile_upload():
    '''
    for uploading csv data in popup
    '''
    file = request.files['file']
    if file:
        user_id = session.get('loginid')

        filename = secure_filename(file.filename)
        _path = os.path.join(root_path, "customers", user_id, "data_files",filename)
        file.save(_path)

    return redirect(url_for('api'))

@app.route('/datafile_delete', methods=['GET','POST'])
def datafile_delete():
    '''
    for deleting csv data in popup
    '''
    text = request.form['delete_file']
    if text:
        user_id = session.get('loginid')

        _path = os.path.join(root_path, "customers", user_id, "data_files",text)
        os.remove(_path)

    return redirect(url_for('api'))

@app.route('/load_globs', methods=['GET','POST'])
def load_globs():
    '''
    load the glob.html in popup
    '''
    user_id = session.get('loginid')
    id_path = os.path.join(root_path,"customers",user_id)

    data_path = os.path.join(id_path, "data_files")
    datas = os.listdir(data_path)

    return render_template("globs.html", datas=datas, user_id=user_id)




@app.route('/get_user_id',methods=['GET','POST'])
def get_user_id():
    uid = session.get('loginid',None)
    return uid



########################################

@app.route('/progresbar_html')
def progresbar_html():
    '''
    trace the model train time
    '''
    return render_template('progresbar.html')



@app.route('/generate_progress')
def generate_progress():
    '''
    for rendering the model train progress bar until finishing whole train epochs
    '''
    uid = session.get('loginid', None)
    tpath = os.path.join(root_path, 'customers', uid, 'progress.txt')
    generate = partial(progress_bar_generate,tpath)
    return Response(generate(), mimetype='text/event-stream')




if __name__ == "__main__":
    app.config['SECRET_KEY'] = 'i am a secret HyukHun'

    csrf = CSRFProtect()
    csrf.init_app(app)

    app.run(host=host_addr, port=port_num, debug=True)
