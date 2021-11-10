"""
MVC
Model : 데이터베이스 연결
View : 클라언트가 보는 부분
controller : 접근 url에 따라 연결


html 주소 가져오기 : getbootstrap.com

---1 모델을 다루는 법(DB)
sqlalchemy : model 지원

db = SQLAlchemy(app)
#mysql로 하는 법?

class Test(db.Model): # test는 하나의 모델이 되어서 db에 데이터를 넣고 뺄 수 있음
        # 스키마 설정
        __tablename__ = 'test_table' # 테이블명 지정
        # 컬럼 만들기
        id = db.Column(db.Integer, primary_key = True)
        name = db.Column(db.String(32), unique = True)

db.create_all() # 모델클래스 등록


--2 탬플릿을 다루는 패키지 : jinja
    render_templates(html)


--3 get, post
    get요청은 페이지를 가져오고
    post요청은 클릭을 눌렀을 때 데이터를 가져오는 것
    get : html
    post : redirect('주소')

    db 사용
        db.init_app(app)
        db.session.add(db.class)
        db.session.commit()


--4 form 관리 <패키지 : Flask-WTF > : csrf와 validation 사용가능하게 함
    + csrf 보호기법 사용 가능
        -사이트 간 요청 위조 방지
        -form 안에 암호화된 hash키 넣어놓고 비교하게 하는 것
    python :
        csrf = CSRPROTECT()
        csrf.init_app(app)


    form 및 csrf - python에서 만든 클래스 안의 변수 이름들을 사용
        python :
            render_templates(html, form)으로 form을 html로 전달
        html :
            <form method="POST">
            {{form.csrf_token}}
            <div class="form-group>
            {{form.userid.label("아이디")}} # 라벨사용
            {{form.userid(class='form-control',placeholder="아이디")}} </div>
                 - 속성값 지정
                 - 원하는 속성값에 이름 할당 후 빈칸에 나타날 값 필요하면 placeholder사용
            <div class="form-group>
            {{form.username.label("사용자이름")}} # 라벨사용
            {{form.username(class='form-control',placeholder="아이디")}} </div> </form>


    + validation 검증 가능
    python :
        form.py : form class 안에서
        userid = StringField('userid', validators=[DataRequired(),EqualTo('필드네임')])
            - 데이터가 들어왔는지 안들어왔는지 확인하는 것이 validator
            - datarequired : 데이터 필수로 들어와야 함
            - equal to : 다른 필드와 같은지(비밀번호,비밀번호재확인 같은지)
        app.py :
        form = flaskform()
        form.validate_on_submit()으로 post요청과 값이 잘 들어왔는지, 값이 정상적인지 확인 가능하게 됨


--5 static 파일 관리 : javascript,css,img파일 등등
    static:폴더 만들기
        html :
            <link rel="stylesheet" href="{{ url_for('static',filenmae='style.css}}">
            # 이런식으로 url_for을 써서 경로 지정해서 링크 가능


--6 세션
    홈페이지 접속
        - 처음 세션 요청시 쿠키가 없음(세션 시작)
        - 그래서 홈페이지가 뜨면 서버자체에  db에 쿠키 저장 후 cookie를 받아서 브라우저 쿠키 공간에 저장함
    홈페이지 접속 뒤 실행
        - 쿠키를 가지고 다시 요청하게 되고, 그것으로 정보 유지
        - 쿠키 만료시간이 지나면 접속이 끊기고 세션 종료

    python :
        작동 url ( /login)
        if form.validate_on_submit():
            session['userid'] = form.data.get('userid') -- 세션시작

        홈페이지 url ( /)
        @app.route('/')
        def hello():
            userid = session.get('userid', None) # session에서 userid를 받고 만약 없으면 None
            return render_template('hello.html',userid=userid) # cookie
                - 자동으로 클라이언트 나눠서 할당하기 때문에 사용자별로 다른 userid가 cookie로 들어감

        forms.py :
        class LoginForm(flaskform):
            class UserPassword(object):
                def __init__(self,message=None):
                    self.message = message

                def __call__(self, form, field):
                    userid = form['userid'].data
                    password = field.data

                    # dbname = dbname.query.filter_by(userid=userid).first()
                    # if 패스워드 다르면:
                    #     raise 에러
            userid = StringField('userid', validators=[DataRequired(),EqualTo('필드네임'), UserPassword()])
        - 이런식으로 따로 validator 만들고 userid 관련 에러가 나면 에러사항을 html에서
        - {{ form.userid.error.0 }} 으로 출력



    html : userid대신 password에러 예시

         login.html :
         <div class="form-group">
                {{ form.password.label("비밀번호") }}
                {% if form.password.erros %}
                {{ form.password.errors.0 }}
                    - form의 해당 변수관련해서 에러날 때마다 errors리스트 에 저장
                    - 인덱스를 .0, .1등으로 사용
                {% endif %}
                {{ form.password(class="form-control", placeholder="비밀번호") }}
              </div>


         hello.html
         <a href="/logout"> 로그아웃</a> 링크 추가로 로그아웃연결

-- 7 REST 소개
    웹페이지 refresh 거의 없게 하기 위해 백엔드-프론트엔드 분리
    그러려면 벡엔드에서 UI제거

    RESTFUL API
        - 규약 : 컬렉션/항목/컬렉션 // uri 리소스만 넣고 동작은 http로 method로 해라
        - 주소에 따라 어떤 데이터를 반환할 것인지
            - GET : 리소스 가져오는 것
            - POST : 리소스 생성
            - PUT : 리소스 대체하는 경우 많이 씀(업데이트도 쓰임)
            - PATCH : 리소스 업데이트
            - DELETE : 제거


-- 8 복습 및 개선
    Blueprint 이용
        - blueprint 객체를 생성한다.
        - app을 정의하는 함수(app = Flask(__name__)이 포함된)에서 app에 blueprint 객체를 register해준다.
        - controller route에서 blueprint 객체를 써준다.

        - 절차
            딕렉토리 분할수 api 만들고 __init__에 Blueprint 생성하고
            다른 파일에서 api.route('/') 만들고
            본 app.py에서 app.register_blueprint('api',url_prefix='')넣어준다.

    db 시리얼라이즈
        @property이용
            ex)     #직렬활용
                    @property
                    def serialize(self):
                        return {
                            'id' : self.id,
                            'password' : self.password,
                            'userid' : self.userid,
                            'username' : self.username
                            }



        request.get_json()

-- 9 ajax, jquery


    -- jquery
    : Get the <button> element with the class 'continue' and change its HTML to 'Next Step...'
    $( "button.continue" ).html( "Next Step..." )

    : Event Handling
    - Show the #banner-message element that is hidden with display:none in its CSS when any button in #button-container is clicked.

    var hiddenBox = $( "#banner-message" );
    $( "#button-container button" ).on( "click", function( event ) {
      hiddenBox.show();
    });

    -- Ajax : 비동기 요청, 화면전환없이 요청 가능
    - Call a local script on the server /api/getWeather with the query parameter zipcode=97201 and replace the element #weather-temp's html with the returned text.

    $.ajax({
      url: "/api/getWeather",
      data: {
        zipcode: 97201
      },
      success: function( result ) {
        $( "#weather-temp" ).html( "<strong>" + result + "</strong> degrees" );
      }
    });

        추가 후 실행
        <script
          src="https://code.jquery.com/jquery-3.5.1.min.js"
          integrity="sha256-9/aliU8dGd2tb6OSsuzixeV4y/faTqgFtohetphbbj0="
          crossorigin="anonymous">

          </script>

        ex)    function regist(){
                $.ajax({
                url: 'api/v1/user_detail',
                contentType : 'application/json',
                method : 'POST',
                data : JSON.stringify({
                  userid : $('#userid').val(),
                  username : $('#usernaem').val(),
                  password : $('#password').val(),
                  're-password' : $('#re-password').val()})
                })
                .done(function (res){
                  alert('성공')
                  window.location = '/'; // 이동
                   })
                }

-- 9 token 방식 인증 - jwt사용 == Flask-JWT
    - 기능
        : 자동으로 인증 url 생성, 토큰 생성, 유효성 검사 자동


    app.py
        ## 로그인 할 때 브라우저 쿠키에 토큰 인증키 넣기
        def authenticate(username, password):
            user = Fcuser.query.filter(Fcuser.userid==username).first()
            if user.password == password:
                return user

        ## 인증하고나서 사용자가 또 토큰을 전달했을 때 user정보를 변환하는 함수가 필요한데, 그 역할을 하는 함수
        def identity(payload): # id값이 identity에 들어있음
            userid = payload['identity']
            return  Fcuser.query.filter(Fcuser.userid==userid).first()

        jwt = JWT(app, authenticate, identity)


    api.py
        @jwt_required()를 @api.route밑에 넣기 그러면 인증된 사용자만 api사용 가능


    home.html
         $(document).ready(function () { // 문서가 로딩 되었을 때 자동 실행해라
        if($.cookie('access_token')){
        $("#logout-div").show();}
        else{
        $("#logout-div").hide();
        }

       $.ajax({
        url: '/api/v1/users',
        contentType: 'application/json',
        method: 'GET',
        beforeSend : function(xhr){
            xhr.setRequestHeader('Authorization','JWT ' + $.cookie('access_toekn'))
            }
          }).done(function (res)({
          $.("#content").text(res); // 해당 칸에 text넣기
        }).error(function (res){
          window.location = '/login';
        });

       function logout()
       {
        $.removeCookie('access_token');
        window.location = '/login';
       }


    login.html
        function login(){
          $.ajax({
          url: /auth',  //자동으로 url생성되어 적용 됨
          contentType : 'application/json',
          method : 'POST',
          data : JSON.stringify({
            userid : $('#username').val(),
            password : $('#password').val()})
          })
          .done(function (res){
            $.cookie('access_token', res.access_token); // cookie에 토큰 저장
             })
          }


"""


"""
# 시간마다 진행
#from apscheduler.schedulers.background import BackgroundScheduler
# def get_status(train_model_name,uid):
#       '''여기에 하고 싶은 함수를 쓰세요'''
#     confirm_path = os.path.join(root_path,"customers",uid,train_model_name)
#     check = os.path.isfile(confirm_path)
#     if check:
#         res = "완료"
#         sched.shutdown()
#     else:
#         res = "진행중"
#     return res
#
# sched = BackgroundScheduler(daemon=True)
# sched.add_job(lambda: get_status(train_model_name,uid), 'interval', seconds=60)
# sched.start()
#

#### login session time period make
# @app.route('/db_')
# ##for login timeout#####
# login_mgr = LoginManager(app)
# login_mgr.login_view = 'login'
# login_mgr.refresh_view = 'relogin'
# login_mgr.needs_refresh_message = (u"Session timedout, please re-login")
# login_mgr.needs_refresh_message_category = "info"
# @app.before_request
# def before_request():
#     session.permanent = True
#     app.permanent_session_lifetime = timedelta(minutes=20)
# ###########

"""

"""
### form validation 사용법###
    # if aiform.validate_on_submit():
    #     epochs = aiform.epochs.data
    #     lr = aiform.lr.data
    #     bs = aiform.bs.data
    #     print(epochs,lr,bs)
    #
    # if dtform.validate_on_submit():
    #     print("ok")

"""