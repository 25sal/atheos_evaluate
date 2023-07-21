from flask import render_template, redirect, url_for, flash, request, session, make_response, Blueprint
from  app.models import base
from app.models import db
from app.models.base import Users
from app.forms import LoginForm, RegistrationForm
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash 
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from app.models.base import getproject, getexercises, getexercisefolder, getchecks, getexercisetext, savechecks, savetestresult
import json
import glob
import os
import time, calendar
from app.config import Config
import shutil
from app.checker import Checker
import logging
from sqlalchemy import text

logger = logging.getLogger(__name__)
logging.basicConfig()

login_manager=LoginManager()

user_bp =  Blueprint('user_bp', __name__)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Route
@user_bp.route('/', methods=['GET','POST'])
def index():
    form = LoginForm()
    if current_user.is_authenticated :
        return redirect(url_for('user_bp.languageselector'))
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password,form.password.data):
                if form.remember_me.data:
                    login_user(user, remember=True, duration=timedelta(days=30))
                else:
                    login_user(user, remember= False)
                session['userid'] = user.id
                session['username'] = user.email

                return redirect(url_for('user_bp.languageselector'))
            else:
                flash("Oops! Invalid password. Please try again later.")

        else:
            flash("Oops! User doesn't exist.")
    return render_template('index.html', form = form)



# Route
@user_bp.route('/atheos_login', methods=['POST'])
def atheos_login():

    user_id = request.form.get("user_id")
    access_token = request.form.get("access_token")
    secret = request.form.get("secret")

    if user_id is None or access_token is None or secret is None:
        return "Missing required parameters."
    if current_user.is_authenticated:
        return "already authenticated"
    if secret == "my-secret":
        user = Users.query.filter_by(email=user_id).first()
        if user:
                base.saveAccessToken(access_token,user.id)
                login_user(user, remember=True, duration=timedelta(days=30))
                session['userid'] = user.id
                session['username'] = user.email
                print(user.email)
                return "logged successful"
        else:
            flash("Oops! User doesn't exist.")
            return "Oops! User doesn't exist."





@user_bp.route('/register', methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        email = Users.query.filter_by(email=form.email.data).first()
        if email is None:
            hashed_pw= generate_password_hash(form.password_hash.data,"sha256")
            user = Users(email=form.email.data,password=hashed_pw)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('user_bp.index'))
        else:
            flash("Oops! User already exist.")
    return render_template('register.html', form=form)

@user_bp.route('/logout', methods=["GET"])
@login_required
def logout():
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    flash("Arrivederci")
    return redirect(url_for('user_bp.index'))

@user_bp.route('/languageselector')
@login_required
def languageselector():
    return render_template('languageselector.html')

@user_bp.route('/setoptions', methods=['GET','POST'])
@login_required
def setoptions():
    if request.method == "POST":
        if(request.form.get('language')):
            session["language"] = request.form.get('language')
            exercises = getexercises(session["language"],0)

            session["exercise"] = exercises[0][0]
        parametro = {"language":session["language"],"exercise":session["exercise"]}
        return json.dumps(parametro)
    else:
        return {"language":"c","exercise":1}

@user_bp.route('/test')
@login_required
def test():
    return render_template('test.html')

@user_bp.route('/listexercise', methods = ['GET','POST'])
@login_required
def listexercise():
    dizionario = {}
    lista = []
    if request.method == "POST":
        exercises = getexercises(session["language"],0)
        for exercise in exercises:
            dizionario['value'] = exercise[0]
            dizionario['text'] = exercise[2]
            lista.append(dizionario)
            #verifico cosa passa

        return json.dumps(lista)
    return json.dumps({})
        
@user_bp.route('/testgrid', methods = ['GET','POST'])
@login_required
def test_grid():
    isexam = 0
    exId = 0
    if 'exams' in session.keys():
        isexam=1
        exId = getproject(session["username"])
        session["exercise"] = exId['idproject']
        session["language"] = exId['language']
    elif 'exercise' in session.keys():
        exId = session["exercise"]
    else:
        session["exercise"] = 1;
        
    exer_folder = getexercisefolder(exId['idproject'],isexam)
    user_folder =Config.users_dir+"/"+session["username"]+"/"+str(exer_folder[0])


    if not os.path.isdir(user_folder):
        os.makedirs(user_folder, 0o755, True)
        os.system("cd "+user_folder+"&&git init > /dev/null")
        os.system("cd "+user_folder+'&&git config  user.email "platform@localhost"')
        os.system("cd "+user_folder+'&&git config  user.name "platform"')

        if os.path.isdir(Config.data_dir+"/exercises/"+str(exer_folder[0])+"/template"):
            files = glob.glob(Config.data_dir+"/exercises/"+str(exer_folder[0])+"/template/*")
            for file in files:
                if os.path.isfile(file):
                    shutil.copy(file, user_folder+"/"+os.path.basename(file))
                else:
                    print(file)
        os.system("cd "+user_folder+"&&git add *."+session["language"])
        os.system("cd "+user_folder+'&&git commit -a -m "first commit" > /dev/null')



    page = '<?xml version = "1.0" encoding="UTF-8"?>'
    page += '<rows><head>'
    page += '<column id="c1" width="*" type="ro" align="left" sort="str">Filename</column>'
    page += '<column id="c2" width="*" type="ro" align="left" sort="str">Date</column>'
    page += '</head>'

    files = glob.glob(user_folder+"/*")
    i = 1
    for file in files:
        if file.endswith(session["language"]) or file.endswith(".txt") :
            page += '<row id="'+str(i)+'"><cell>'+os.path.basename(file)+'</cell>'
            fmdate =  os.path.getmtime(file)
            page += '<cell>'+time.strftime("%F %d %Y %H:%i:%s.", time.gmtime(fmdate))+'</cell></row>'
            i += 1

    page += '</rows>'
    resp = make_response(page)
    resp.headers['Content-Type'] = 'application/xml'
    return resp

@user_bp.route('/testtoolbar', methods = ['GET','POST'])
@login_required
def toolbar():
    page = '<?xml version="1.0" encoding="UTF-8"?>'
    page += '<toolbar>'
    page += '<item id="account" type="buttonSelect" img="./account.png" imgdis="./account.png" text="Account" action="showNewDocumentSelect">'
    page += '<item type="button" id="logout" text="Logout" img="./logout.jpeg" action="doOnNewDocument"/> </item>'
    page += '<item id="language" type="buttonSelect" img="./language.jpeg" imgdis="./language.jeg" text="Choose Language"  action="showNewDocumentSelect">'
    page += '<item type="button" id="vhdl" text="vhdl" img="./vhdl.jpeg"  action="setLanguage"/>'
    page += '<item type="button" id="c" text="c" img="./c.png" 	action="setLanguage"/>'
    page += '<item type="button" id="cpp" text="c++" img="./c++.jpeg" action="setLanguage"/> </item>'
    page += '<item id="info" type="button" text="Info" img="./help.gif"/>'
    page += '<item id="info" type="button" text="'+current_user.email+'" /> </toolbar>'
    resp = make_response(page)
    resp.headers['Content-Type']='application/xml'
    return resp

@user_bp.route('/testform', methods = ['GET','POST'])
@login_required
def testform():

    # checks = getchecks(session['username'])
    checks = {}
    submit = "true"
    msg_consegna = "Manca upload della soluzione"
    if 'uploaded' not in checks.keys():
        msg_consegna="Manca upload della soluzione"
    elif 'built' not in checks.keys():
        msg_consegna="Il programma non compila"
    elif 'execution' not in checks.keys():
        msg_consegna="Il programma non esegue"
    elif 'outfile' not in checks.keys():
        msg_consegna="Il file output.bin non è stato mai creato"
    else:
        submit="false"
    if 'test' not in checks.keys() or checks['test']==0:
        msg_consegna="Consegna abilitata, ma nessun test concluso con successo"
    else:
        msg_consegna="Consegna incoraggiata, almeno un test concluso con successo"

    if 'exercise' in session.keys():
        exId = session['exercise']
    else:
        session["exercise"] = 1

    tp = "Nessun test eseguito"
    tf = "Nessun test eseguito"
    '''
    results = getresults(current_user.id, session["exercise"])
    if ((results[0]+results[1]) != 0)
        tp = results[0]
        tf = results[1];
    '''

    page = '<?xml version="1.0" encoding="UTF-8"?>'
    page += '<items>'
    page += '<item type="settings"  labelWidth="80" inputWidth="150" position="absolute" />'
    page += '<item type="button"  name="Test" label="Test" value="Test" width="250" inputLeft="5" inputTop="20" />'
    page += '<item type="input"  name="tp" label="Test Passed" value="'+tp+'"  labelWidth="250" labelAlign="left" labelLeft="275" labelTop="5" inputLeft="275" inputTop="21" />'
    page += '<item type="input"  name="tf" label="Test Failed" value="'+tf+'" labelWidth="150" readonly="true" tooltip="Number of" info="true" labelLeft="550" labelTop="5" inputLeft="550" inputTop="21" />'
    page += '<item type="btn2state"  name="consegna" label="Consegna" labelWidth="150" labelLeft="5" labelTop="80" inputLeft="80" inputTop="74" disabled="'+submit+'" tooltip="consegna abilitata se il programma crea il file output.bin" info="true"  />'
    page += '<item type="label"  name="msg_consegna" label="'+msg_consegna+'" labelLeft="140" labelTop="75" inputLeft="80" inputTop="74" labelWidth="200" />'
    page += '<item type="input" name="testlog" label="Test Output" rows="36" value="" width="1050" inputTop="150" labelTop="130" readonly="true" />'
    page += '</items>'
    resp = make_response(page)
    resp.headers['Content-Type'] = 'application/xml'
    return resp

@user_bp.route('/checks', methods = ['GET','POST'])
@login_required
def checks():
    if "exams" in session.keys():
        checks = getchecks(session['username'])
    else:
        checks = getchecks(session['username'], session["exercise"]);

    if checks is  None:
        checks ={}

    if session["language"] == "c" or  session["language"] == "cpp":
        page = "<html><body><table><tr>"
        uploaded = False
        if 'uploaded' in checks.keys():
          page += '<td><img style="width:20%;vertical-align: middle" src="/static/codebase/imgs/checked.gif" />uploaded</td>'
          uploaded = True
        else:
          page += '<td><img style="width:17%;vertical-align: middle" src="/static/codebase/imgs/unchecked.gif" />not uploaded</td>'
        if uploaded and 'built' in checks.keys() and checks['built'] != 0:
          page += '<td><img style="width:20%;vertical-align: middle" src="/static/codebase/imgs/checked.gif" />compiled</td>'
        else:
            page += '<td><img style="width:17%;vertical-align: middle" src="/static/codebase/imgs/unchecked.gif" />not compiled</td>'
        if uploaded and 'execution' in checks.keys() and checks['execution'] != 0:
            page += '<td><img style="width:20%;vertical-align: middle" src="/static/codebase/imgs/checked.gif" />execution ok</td>'
        else:
            page += '<td><img style="width:17%;vertical-align: middle" src="/static/codebase/imgs/unchecked.gif" />runtime error</td>'
        if uploaded and 'outfile' in checks.keys() and checks['outfile'] != 0:
            page += '<td><img style="width:20%;vertical-align: middle" src="/static/codebase/imgs/checked.gif" />output.bin</td>'
        else:
            page += '<td><img style="width:17%;vertical-align: middle" src="/static/codebase/imgs/unchecked.gif" />no output.bin</td>'
        if uploaded and 'test' in checks.keys() and checks['test'] != 0:
            page += '<td><img style="width:20%;vertical-align: middle" src="/static/codebase/imgs/checked.gif" />'+str(checks['test'])+' test passed</td>'
        else:
            page += '<td><img style="width:17%;vertical-align: middle" src="/static/codebase/imgs/unchecked.gif" />tests failed</td>'
        page += "</tr></table></body></html>"
        resp = make_response(page)
        # resp.headers['Content-Type'] = 'application/xml'
        return resp

@user_bp.route('/deadline', methods = ['GET','POST'])
@login_required
def deadline():
    return str(calendar.timegm(time.gmtime())+7200)
# in setoptions non deve passare l'intera lista ma l'id


@user_bp.route('/exec', methods = ['GET','POST'])
@login_required
def exec():
    if "exercise" not in session.keys():
        session["exercise"] = getexercises(session["language"], 0)[0][0]
    isexam = 0;
    if 'exams' in session.keys() and session["exams"]==1:
        isexam = 1

    exer_folder = getexercisefolder(session['exercise'], isexam)[0]
    user_folder = Config.users_dir + "/" + session["username"] + "/" + exer_folder
    ex_folder = Config.data_dir+'/exercises/'+exer_folder
    logger.debug(session["language"], user_folder, ex_folder)
    checker = Checker(session['username'],session["language"],session["exercise"])
    results = checker.check(session["language"], user_folder, ex_folder )
    logger.debug(checker.checks)
    # save checks
    for key in checker.checks.keys():
        savechecks(session['username'], key, checker.checks[key],session["exercise"])
    if session["language"] == 'c' or session["language"] == 'cpp':
        savetestresult(base.get_userid(session["username"]), results[1:], session["exercise"])
    return results[0]




@user_bp.route('/exercise', methods = ['GET','POST'])
@login_required
def exercise():
    if "exercise"  not in session.keys():
        session["exercise"]=getexercises(session["language"],0)[0][0]

    isexam=0;
    if 'exams' in session.keys():
        isexam=1
    return getexercisetext(session["exercise"],isexam)




@user_bp.route('/results', methods = ['GET','POST'])
@login_required
def results():
    if "exercise" not in session.keys():
        session["exercise"] = getexercises(session["language"], 0)[0][0]
    isexam = 0;
    if 'exams' in session.keys() and session["exams"]==1:
        isexam = 1
    results = db.getresults(db.get_userid(session["username"]),session["exercise"])
    if results[0]+results[1] == 0:
        tp = "Nessun test eseguito"
        tf = "Nessun test eseguito"
    else:
        tp = results[0]
        tf = results[1]

    if 'exams' in session.keys():
        checks = db.getchecks(session['username'])
    else:
        checks = db.getchecks(session['username'],session["exercise"])

    if checks is None:
        checks = {}

    checks['tp'] = tp
    checks['tf'] = tf
    return json.dumps(checks)

@user_bp.route('/upload', methods = ['GET','POST'])
@login_required
def upload():
    if "exercise" not in session.keys():
        session["exercise"] = getexercises(session["language"], 0)[0][0]
    isexam = 0;
    if 'exams' in session.keys() and session["exams"]==1:
        isexam = 1


    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        exer_folder = getexercisefolder(session['exercise'], 0)
        user_folder = Config.users_dir + "/" + session["username"] + "/" + str(exer_folder[0])
        if session['language'] == "c":
            dest_filename = 'main.c'
        elif session['language'] == "cpp":
            dest_filename = 'main.cpp'
        uploaded_file.save(user_folder+"/"+dest_filename)
        os.system("cd " + user_folder + "&&git add *." + session["language"])
        os.system("cd " + user_folder + '&&git commit -a -m "file uploaded" > /dev/null')
        if isexam == 1:
            base.savechecks(session["username"], "uploaded", 1)
        else:
            base.savechecks(session["username"], "uploaded", 1, session["exercise"])
    return "0"

@user_bp.route('/download', methods = ['GET','POST'])
@login_required
def download():
    if "exercise" not in session.keys():
        session["exercise"] = getexercises(session["language"], 0)[0][0]
    isexam = 0;
    if 'exams' in session.keys() and session["exams"]==1:
        isexam = 1

    filename =  request.args.get('filename')
    if filename is not None:
        basename = os.path.basename(filename)
        exer_folder = getexercisefolder(session['exercise'], 0)
        user_folder = Config.users_dir + "/" + session["username"] + "/" + str(exer_folder[0])
        if os.path.isfile(user_folder+"/"+basename):
            resp = make_response(open(user_folder+"/"+basename, 'r').read())
            resp.headers['Content-Type'] = 'plain/txt'
            resp.headers['Content-Disposition'] = 'inline; filename='+basename
            return resp
    return ""



@user_bp.route('/delete', methods = ['GET','POST'])
@login_required
def delete():
    if "exercise" not in session.keys():
        session["exercise"] = getexercises(session["language"], 0)[0][0]
    isexam = 0;
    if 'exams' in session.keys() and session["exams"] == 1:
        isexam = 1
    if 'filename' in request.form.keys():
        filename = request.form.get('filename')
        if filename is not None:
            basename = os.path.basename(filename)
            exer_folder = getexercisefolder(session['exercise'], 0)
            user_folder = Config.users_dir + "/" + session["username"] + "/" + str(exer_folder[0])
            if os.path.isfile(user_folder + "/" + basename):
                os.remove(user_folder + "/" + basename)
    return ""



