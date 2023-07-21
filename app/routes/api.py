from flask import render_template, redirect, url_for, flash, request, session, make_response, Blueprint, jsonify
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
from flask_jwt import JWT, jwt_required, current_identity
logger = logging.getLogger(__name__)
logging.basicConfig()

login_manager=LoginManager()

api_bp =  Blueprint('api_bp', __name__)

jwt = ''

def set_app(app):
    global jwt
    app = app
    jwt = JWT(app, authenticate, identity)


def authenticate(email):
    user = Users.query.filter_by(email=email).first()
    return user
    
def identity(payload):
    user_id = payload['identity']
    return Users.query.get(user_id)



@api_bp.route('/auth_token', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('user_id')

    # Verifica le credenziali e genera il token JWT
    user = authenticate(email)
    if user:
        access_token = jwt.jwt_encode_callback(user)
        user = Users.query.filter_by(email=email).first()
        base.saveAccessToken(access_token,user.id)
        return jsonify({"access_token": str(access_token)})
    else:
        return jsonify({"message": "Invalid credentials"}), 401






@api_bp.route('/exercise_atheos', methods = ['GET','POST'])
@jwt_required()
def exercise():
    exId = getproject(current_identity.email)
    #isexam = 0;
    #if 'exams' in session.keys() and session["exams"]==1:
    #    isexam = 1
    extext = getexercisetext(exId['exercise'],1) #TODO: quando implementiamo di nuovo le esercitazioni sostituire 1 con isexam
    return jsonify({"htmlpage": str(extext)})



@api_bp.route('/exec_atheos', methods = ['GET','POST'])
@jwt_required()
def exec():
    #if "exercise" not in session.keys():
    #    session["exercise"] = getexercises(session["language"], 0)[0][0]
    #isexam = 0;
    #if 'exams' in session.keys() and session["exams"]==1:
    #    isexam = 1
    exId = getproject(current_identity.email)
    exer_folder = getexercisefolder(exId['exercise'], 1)[0]  #TODO: quando implementiamo di nuovo le esercitazioni sostituire 1 con isexam
    user_folder = Config.users_dir + "/" + current_identity.email + "/" + exer_folder
    ex_folder = Config.data_dir+'/exercises/'+exer_folder
    logger.debug(session["language"], user_folder, ex_folder)
    checker = Checker(current_identity.email,exId["language"],exId["exercise"])
    results = checker.check(exId["language"], user_folder, ex_folder )
    logger.debug(checker.checks)
    # save checks
    for key in checker.checks.keys():
        savechecks(current_identity.email, key, checker.checks[key],exId["exercise"])
    if exId["language"] == 'c' or exId["language"] == 'cpp':
        savetestresult(base.get_userid(current_identity.email), results[1:], exId["exercise"])
    return results[0]



@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))



@api_bp.route("/build", methods = ['POST'])
@jwt_required()
def build():
    exId = getproject(current_identity.email)
    exer_folder  = getexercisefolder(exId['idproject'], Config.exams)
    user_folder = Config.users_dir + "/" + current_identity.email + "/" + str(exer_folder[0])
    logs = ""
    if os.path.isdir(user_folder):
        checker = Checker(current_identity.email,exId["language"],exId['idproject'])
        logs = checker.c_builder(user_folder, exer_folder)
        for key in checker.checks.keys():
            savechecks(current_identity.email, key, checker.checks[key], exId['idproject'])
    return logs



