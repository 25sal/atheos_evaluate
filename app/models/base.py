from app.models import db
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import text

# Models
class Users(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(128), nullable = False)
    access_token = db.Column(db.String(128), nullable = True)
    created_at = db.Column(db.DateTime, default=datetime.now())

class Users_results(db.Model):
    __tablename__ = 'users_results'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable = False)
    result = db.Column(db.LargeBinary)
    score = db.Column(db.Integer,default= None)
    success = db.Column(db.SmallInteger,default=0, nullable = False)
    datetime = db.Column(db.DateTime, default=datetime.now(), nullable = False)
    isexam = db.Column(db.SmallInteger,default=0)

class Test_results(db.Model):
    __tablename__ = 'test_results'
    id = db.Column(db.Integer, primary_key=True)
    passed = db.Column(db.SmallInteger)
    failed = db.Column(db.SmallInteger)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    datetime = db.Column(db.Time, default=datetime.time(datetime.now()), nullable = False)
    exercise = db.Column(db.Integer, db.ForeignKey('exercises.id'), default= 0)

class Reserved_users(db.Model):
    __tablename__ = 'reserved_users'
    user =  db.Column(db.String(64), primary_key=True)
    password = db.Column(db.String(128), nullable = False)
    first_name = db.Column(db.String(64))
    second_name = db.Column(db.String(64))
    email = db.Column(db.String(64), nullable = False)
    datetime = db.Column(db.DateTime, default=datetime.now())
    checked = db.Column(db.Integer)
    reset_passwd = db.Column(db.SmallInteger)


class Projects(db.Model):
    __tablename__ = 'projects'
    idexams = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(64), key = 'user_id', nullable = False)
    exercise = db.Column(db.Integer, db.ForeignKey('exercises.id'))
    description = db.Column(db.Text)
    name = db.Column(db.String(45))
    language = db.Column(db.String(45))
    checked = db.Column(db.Integer)


class Exercises(db.Model):
    __tablename__ = 'exercises'
    id = db.Column(db.Integer, primary_key=True)
    folder = db.Column(db.String(45), nullable = False)
    language = db.Column(db.String(45), nullable = False)
    visible = db.Column(db.SmallInteger, default=0, nullable = False)
    description = db.Column(db.LargeBinary)
    isexam = db.Column(db.SmallInteger, default=0)
    title =  db.Column(db.String(45), default='noname')


class Dynamic_exams(db.Model):
    __tablename__ = 'dynamic_exams'
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, nullable = False)
    serial_number = db.Column(db.String(40), nullable = False)
    task = db.Column(db.String(40), nullable = False)
    project_id = db.Column(db.String(40), nullable = False)

class Connections(db.Model):
    __tablename__ = 'connections'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(50), default= None)
    user = db.Column(db.String(45), default= None)
    cookie = db.Column(db.String(45), default= None)
    time = db.Column(db.Time, default= datetime.time(datetime.now()), nullable = False)

class Checks(db.Model):
    __tablename__ = 'checks'
    id = db.Column(db.Integer, primary_key=True)
    id_exam = db.Column(db.Integer, nullable = False)
    parameter = db.Column(db.String(20), default= '0', nullable = False)
    value = db.Column(db.SmallInteger, default= 0, nullable = False)
    
class Admins(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(20), nullable = False) 
    password = db.Column(db.String(40), nullable = False)
    first_name = db.Column(db.String(20))
    second_name = db.Column(db.String(20))
    email = db.Column(db.String(40), nullable = False)

# Operations

def getCSVList():
    t = text("SELECT * FROM CSV")
    result = db.session.execute(t)
    result_list = list(result)
    return result_list

def getCSV(id):
    t = text("SELECT * FROM CSV")
    result = db.session.execute(t, {'val': id})
    return result

def getSimulationIds(day):
    month = 0
    if(day[1] == 'January'):
        month = 1
    elif(day[1] == 'February'):
        month = 2
    elif(day[1] == 'March'):
        month = 3
    elif(day[1] == 'April'):
       month = 4
    elif(day[1] == 'May'):
       month = 5
    elif(day[1] == 'June'):
       month = 6
    elif(day[1] == 'July'):
       month = 7
    elif(day[1] == 'August'):
       month = 8
    elif(day[1] == 'September'):
       month = 9
    elif(day[1] == 'October'):
       month = 10
    elif(day[1] == 'November'):
       month = 11
    elif(day[1] == 'December'):
       month = 12

    t = text("SELECT id FROM Simulations where day= :val1 AND month= :val2 AND year= :val3'")
    result1 = db.session.execute(t, {'val1': day[0], 'val2': month, 'val3': day[2]}).fetchall()
    if(result1["id"]):
        t2 = text("SELECT id_sim FROM SimulationCouple where id_giorno= :val")
        result =  db.session.execute(t2,{'val': result1['id']})
        return result
   
def get_userid(username):
    t = text('SELECT id from users where  email= :val')
    result = db.session.execute(t, {'val':username}).fetchall()
    if(result[0]):
        return result[0][0]
    else:
        return None


def getexercises(lang, isexam):
    data = []
    t = text('SELECT id,folder,title FROM exercises where isexam= :val1 and visible=1 and language= :val2 order by id')
    result = db.session.execute(t, {'val1': isexam, 'val2':lang}).fetchall()
    for row in result:
        data.append(list(row))
    return data

def getexercise(id):
    data = []
    t = text('SELECT id,folder,title FROM exercises where id= :val')
    result = db.session.execute(t,{'val':id}).fetchall()
    for row in result:
        data.append(list(row))
    return data

def getexercisefolder(id,isexam):
    t = text('SELECT folder FROM exercises where isexam= :val1 and visible=1 and id= :val2')
    result = db.session.execute(t, {'val1': isexam, 'val2': id}).fetchall()
    if(result):
        return result[0]
    else:
        return None

def getexercisetext(id,isexam):
    t = text('SELECT description FROM exercises where isexam= :val1 and visible=1 and id= :val2')
    result = db.session.execute(t, {'val1': isexam, 'val2': id}).fetchall()
    if(result):
        temp = result[0]
        return temp[0].decode('utf-8')
    else:
        return None
    
def savetestresult( iduser, results, exercise):
    t = text('INSERT INTO test_results (passed, failed, user_id, exercise) VALUES (:val1,:val2,:val3,:val4)')
    db.session.execute(t,{'val1': results[0],'val2': results[1],'val3': iduser,'val4': exercise})
    db.session.commit()
    return True

def getresults(user, exercise):
    t = text('SELECT passed, failed FROM test_results WHERE user_id= :val and exercise=:val1 order by id desc')
    result = db.session.execute(t,{'val': user, 'val1':exercise}).fetchall()
    count = len(result)
    if(count==0):
        return (0,0)
    else:    
        return (result[0][0],result[0][1])

def checkfirstconnection(ip,username,cookie):
    t = text('SELECT user, ip FROM connections WHERE (user=:val)')
    result = db.session.execute(t,{'val':username}).fetchall()
    count = len(result)
    if(count==0):
        t2 = text('INSERT INTO  connections (ip,user,cookie) VALUES (:val1,:val2,:val3)')
        db.session.execute(t2,{'val1':ip,'val2':username,'val3':cookie})
        db.session.commit()
    else:                
        if(ip==result[1]):
            t3 = text('INSERT INTO  connections VALUES(:val1,:val2,:val3')
            db.session.execute(t3,{'val1':ip,'val2':username,'val3':cookie})
            db.session.commit()

def save_checks_test(iduser,exercise, parameter, value):
    t = text('SELECT parameter FROM checks_test where userid=:val1 and exercise=:val2 and parameter=:val3')
    result = db.session.execute(t,{'val1':iduser,'val2':exercise,'val3':parameter}).fetchall()
    count = len(result)
    if(count==0):
        t2 = text('INSERT INTO checks_test  VALUES (:val1,:val2,:val3,:val4)')
        db.session.execute(t2,{'val1':iduser,'val2':exercise,'val3':parameter,'val4':value})
        db.session.commit()
    else:
        t3 = text('UPDATE checks_test set value=:val1 where parameter=:val2 and userid=:val3 and exercise=:val4')
        db.session.execute(t3,{'val1':value,'val2':parameter,'val3':iduser,'val4':exercise})
        db.session.commit()

    return True


def savechecks( iduser, parameter,value, exercise=-1):
    checksaved = False
    if(exercise > 0):
        return save_checks_test(get_userid(iduser),exercise,parameter,value)
    else:
        idproject = getproject(iduser)
    t = text("SELECT parameter FROM checks  where id_exam= :val1 and parameter= .val2")
    db.session.execute(t,{'val1':idproject['idproject'],'val2':parameter}).fetchall()
    count = db.session.rowcount()
    if(count==0):
        t2 = text("INSERT INTO checks  VALUES (:val1,:val2,:val3)")
        db.session.execute(t2,{'val1':idproject['idproject'],'val2':parameter,'val3':value})
        db.session.commit()
    else:
        t3 = text('UPDATE checks set value= :val1 where parameter=:val2 and id_exam=:val3')
        db.session.execute(t3,{'val1':value,'val2':parameter,'val3':idproject['idproject']})
        db.session.commit()
        checksaved = True
    return checksaved

def get_checks_test(iduser, exercise):
    t = text('SELECT parameter,value FROM checks_test  where userid=:val1 and exercise=:val2')
    result = db.session.execute(t, {'val1':iduser,'val2':exercise}).fetchall()

    if len(result)==0:
        return None
    else:
        response = {}
        for res in result:
            response[res[0]]=res[1]
        return response

def getchecks( iduser, exercise=-1):
    if(exercise > 0):
        return get_checks_test(get_userid(iduser),exercise)
    else:
        idproject = getproject(iduser)

    t = text('SELECT parameter,value FROM checks  where id_exam=:val')
    result = db.session.execute(t,{'val':idproject['idproject']}).fetchall()
    count = len(result)
    if(count==0):
        return None
    else:
        response = {}
        for res in result:
            response[res[0]] = result[1]
        return response
        
def getproject(user):
    t = text('SELECT idexams, language, exercise FROM projects  WHERE userid=:val')
    result = db.session.execute(t, {'val':user}).fetchall()
    count = len(result)
    if count == 0:
        return None
    else:

        return {"idexams":result[0][0], "language":result[0][1], 'exercise':result[0][2]}

def checkUsername(username):
    exist = False
    t = text('SELECT id FROM users WHERE email = :val')
    result = db.session.execute(t,{'val':username}).fetchall()
    count = db.session.rowcount()
    if(count==1):
        exist = True
    return exist
 
# create table

def saveAccessToken(access_token, id):
    t = text('UPDATE users set access_token=:val1 where id=:val2')
    db.session.execute(t,{'val1':access_token,'val2':id})
    db.session.commit()



