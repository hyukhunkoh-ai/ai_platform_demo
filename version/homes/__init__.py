import os

from version.api.sql import conn, cursor
from flask import *
from version.forms import Registerform, Loginform, Home, Delete_registerform

from . import homes_utils
from version.config import root_path

homes = Blueprint('homes', __name__)


@homes.route('/', methods=['GET', 'POST'])
def home():
    form = Home()
    loginid = session.get('loginid',None)
    return render_template("home.html", loginid=loginid, form=form)

@homes.route('/register',methods=['GET','POST'])
def register():
    form = Registerform()
    if form.validate_on_submit():
        username = form.data.get('username')
        unique = form.data.get('unique')
        id = username + unique
        query = "INSERT INTO logins (name) VALUES (%s)"
        try:
            cursor.execute(query, id)
            conn.commit()
        except :
            return "이미 있는 아이디 입니다."

        homes_utils.make_directory(id)

        return redirect('/login')

    return render_template("register.html", form=form)


@homes.route('/delete_register',methods=['GET','POST'])
def delete_register():
    uid = session.get('loginid')
    form = Delete_registerform()

    if form.validate_on_submit():
        delete_id = form.data.get('delete_id')

        homes_utils.delete_all_db_info(delete_id)
        homes_utils.delete_directory(delete_id)
        homes_utils.delete_all_redis_info(delete_id)
        session.pop('loginid', None)
        return redirect('/')

    return render_template("delete_register.html", form=form,uid=uid)



@homes.route('/login', methods=['GET', 'POST'])
def login():
    form = Loginform()
    if form.validate_on_submit():
        session['loginid'] = form.data.get('loginid') #session from flask

        return redirect('/')

    return render_template("login.html", form=form)

@homes.route('/logout',methods=['GET','POST'])
def logout():
    session.pop('loginid',None)
    return redirect('/')



@homes.route('/load_css/<css>',methods=['GET','POST'])
def load_css(css):
    path = os.path.join(root_path,'templates')
    return send_from_directory(path, css)