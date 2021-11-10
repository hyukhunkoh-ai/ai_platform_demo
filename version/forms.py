from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
from version.api.sql import cursor


class Registerform(FlaskForm):
    username = StringField('username',validators=[DataRequired()])
    unique = StringField('unique', validators=[DataRequired()])

class Delete_registerform(FlaskForm):
    class Isequal():
        def __init__(self,message=None):
            self.message = message

        def __call__(self, form, field):
            id = form['delete_id'].data
            uid = form['user_id'].data
            if id != uid:
                raise ValueError('<현재 아이디를 입력해주세요.>')

    delete_id = StringField('delete_id', validators=[DataRequired(),Isequal()])
    user_id = StringField('user_id')

class Loginform(FlaskForm):

    class IsLogin(object):
        def __init__(self,message=None):
            self.message = message

        def __call__(self, form, field):
            id = form['loginid'].data
            query = "SELECT * from logins where name='{}'".format(id)

            cursor.execute(query)
            if not cursor.fetchall():
                raise ValueError('no id')


    loginid = StringField('loginid',validators=[DataRequired(),IsLogin()])


class Home(FlaskForm):
    islogin = StringField('islogin')

class Fileform(FlaskForm):
    file_blank = FileField('file_blank', validators=[FileRequired(), FileAllowed(['csv','jpg','png'], 'csv only!')])
    submit = SubmitField('업로드')
# form1 = Fileform()
# if form1.validate_on_submit():
#     filename = form1.file_blank.data.filename
#
#     form1.file_blank.data.save(data_path + '/{}'.format(filename))
#     return redirect('/globs')
class Deleteform(FlaskForm):
    delete_name = StringField('delete_name',validators=[DataRequired()])


class aiform(FlaskForm):
    epochs = StringField('epochs',validators=[DataRequired()])
    lr = StringField('lr(default:1e-2)')
    bs = StringField('bs',validators=[DataRequired()])

class dtform(FlaskForm):
    message = StringField('message')
    submit = SubmitField('엔진추가')

class ailist(FlaskForm):
    ai_list = SelectField('ai_list', choices=[('cpp', 'C++'), ('py', 'Python'), ('text', 'Plain Text')])