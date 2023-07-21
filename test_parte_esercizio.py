from ast import main
from http import client
from io import BytesIO
import os
import unittest
from flask import Config, Flask, redirect, request, session
import pymysql
import pytest
from flask import Flask, url_for
import self
import sqlalchemy
import sqlalchemy_utils
import app
import unittest
import requests
from requests import Request, Session
import json
#from werkzeug.security import check_password_hash
from datetime import timedelta
from app import app
from app.checker import Checker
from app.models import base
from app.models import db
from app.models.base import Users, getchecks, getexercisefolder, getexercises, savechecks
from app.routes.user import results, user_bp
from rich import print
import requests
from bs4 import BeautifulSoup
import json
from flask import url_for
from flask_login import current_user
from flask import session
from werkzeug.datastructures import FileStorage
from unittest.mock import MagicMock
from io import BytesIO

from flask import Config, redirect, session, url_for, request
from werkzeug.security import generate_password_hash



class TestUserRoute(unittest.TestCase):    
   
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        
        
     #Login - Caso Login con Credenziali Corrette    
    def test_login_con_credenziali_valide(self):
        with self.app as client:
            with app.app_context():
                TestUserRoute.deleteUserfromSession()
                hashed_pw = generate_password_hash('ritapolitelli',"sha256")
                user = Users(email='ritapolitelli@gmail.com', password=hashed_pw)
                # self.assertTrue(current_user.is_authenticated)
                db.session.add(user)
                db.session.commit()

                app.config['WTF_CSRF_ENABLED']=False
                # Simuliamo una richiesta POST con dati corretti
                response = client.post('/', data={
                    'email': 'ritapolitelli@gmail.com',
                    'password': 'ritapolitelli',
                    'remember_me': False
                })

                # Controlliamo che lo status della risposta sia 200
                self.assertEqual(response.status_code, 302)
                #Se l'autenticazione è andata a buon fine, saremo indirizzati alla pagina "languageselector"
                response = client.get(url_for('user_bp.languageselector'), follow_redirects=True)
                self.assertEqual(response.status_code, 200)
                # check that the path changed
                print(request.path)
                assert request.path == url_for('user_bp.languageselector')
    
    def deleteUserfromSession():
        db.session.query(Users).delete()

    def test_esercizio_con_errori_compilazione(self):
            with app.app_context():     
            
                TestUserRoute.deleteUserfromSession()
                hashed_pw = generate_password_hash('ritapolitelli',"sha256")
                user = Users(email='ritapolitelli@gmail.com', password=hashed_pw)
                # self.assertTrue(current_user.is_authenticated)
                db.session.add(user)
                db.session.commit()

                app.config['WTF_CSRF_ENABLED']=False
                # Simuliamo una richiesta POST con dati corretti
                with self.app as client:
                    response = client.post('/', data={
                        'email': 'ritapolitelli@gmail.com',
                        'password': 'ritapolitelli',
                        'remember_me': False
                    })
                    self.setUp()
                    
                    # Carica un file di test
                    test_file_path = 'main.c'
                    file_content = """#include <stdio.h>

                                    int main() {
                                    // Errore di compilazione: variabile non dichiarata
                                    x = 10;
                                    printf("Hello, World!");
                                    return 0;
                                    }"""
                                    
                                    
                    with open(test_file_path, 'w') as test_file:
                            test_file.write(file_content)

                        # Simula la sessione per includere le chiavi necessarie
                            with self.app.session_transaction() as session:
                                session['exercise'] = 'esercizio_1'
                                session['language'] = 'c'
                                session['username'] = 'testuser'
                                session['exams'] = False

                        # Effettua la richiesta POST alla route di upload
                                response = self.app.post('/upload', data={
                                 'file': (open(test_file_path, 'rb'), 'main.c')
                                 }, content_type='multipart/form-data', follow_redirects=True)

                        # Verifica che ci siano errori di compilazione
                                self.assertEqual(response.status_code, 200)
                                #self.assertEqual(response.data, b'1')  # Assume che '1' rappresenti un errore di compilazione

                                # Esegue una richiesta GET alla route /checks
                                response = self.app.get('/checks', follow_redirects=True)
                                self.assertEqual(response.status_code, 200)
                                self.assertIn(b'uploaded', response.data)

                                # Esegue una richiesta GET alla route /test
                                response = self.app.get('/test', follow_redirects=True)
                                self.assertEqual(response.status_code, 200)
                                                    

                                # Esegue una seconda richiesta GET alla route /checks
                                response = self.app.get('/checks', follow_redirects=True)
                                self.assertEqual(response.status_code, 200)
                                self.assertIn(b'not compiled', response.data)

    #Caso 2: 1.upload (file main.c, senza errori di compilazione e corpo vuoto), 3.test, 4.check (verificando che il file è build ed exec, ma non output)


    def test_upload_main_c_vuoto(self):
            
            with app.app_context():     
            
                TestUserRoute.deleteUserfromSession()
                hashed_pw = generate_password_hash('ritapolitelli',"sha256")
                user = Users(email='ritapolitelli@gmail.com', password=hashed_pw)
                # self.assertTrue(current_user.is_authenticated)
                db.session.add(user)
                db.session.commit()

                app.config['WTF_CSRF_ENABLED']=False
                # Simuliamo una richiesta POST con dati corretti
                with self.app as client:
                    response = client.post('/', data={
                        'email': 'ritapolitelli@gmail.com',
                        'password': 'ritapolitelli',
                        'remember_me': False
                    })
                    self.setUp()                   

# Carica un file di test
                    test_file_path = 'test_file.txt'
                    file_content = ''
                    with open(test_file_path, 'w') as test_file:
                                test_file.write(file_content)

                                # Simula la sessione per includere le chiavi necessarie
                                with self.app.session_transaction() as session:
                                    session['exercise'] = 'exercise_value'  # Imposta il valore desiderato per 'exercise'

                                    # Effettua la richiesta POST alla route di upload
                                    response = self.app.post('/upload', data={
                                    'file': (open(test_file_path, 'rb'), 'test_file.txt')
                                    }, content_type='multipart/form-data', follow_redirects=True)


                                    # Verifica che il caricamento sia avvenuto con successo
                                    self.assertEqual(response.status_code, 200)

                                    # Verifica che il file sia stato salvato correttamente sul server
                                    exer_folder = getexercisefolder(session['exercise'], 0)[0]
                                    user_folder = Config.users_dir + "/" + session["username"] + "/" + str(exer_folder)
                                    uploaded_file_path = os.path.join(user_folder, 'main.c')
                                    self.assertTrue(os.path.isfile(uploaded_file_path))

                                    # Verifica che il file sia vuoto
                                    with open(uploaded_file_path, 'r') as uploaded_file:
                                        uploaded_file_content = uploaded_file.read()
                                        self.assertEqual(uploaded_file_content, '')

                                    # Verifica che lo stato "uploaded" sia stato salvato correttamente
                                    checks = getchecks(session['username'], session["exercise"])
                                    self.assertIn('uploaded', checks)
                                    self.assertEqual(checks['uploaded'], 1)

                                    # Effettua una richiesta GET alla route 'test'
                                    response = client.get('/test', follow_redirects=True)
                                    self.assertEqual(response.status_code, 200)
                                

                                    # Simula i controlli che indicano che il file è stato caricato, compilato ed eseguito correttamente
                                    checks = {
                                        'uploaded': 1,
                                        'built': 1,
                                        'execution': 1,
                                        'outfile': 0  # Imposta a 0 per indicare l'assenza di output
                                    }
                                    getchecks(session['username'], checks)

                                    # Effettua una richiesta GET alla route 'checks'
                                    response = client.get('/checks', follow_redirects=True)

                                    # Verifica che la risposta sia stata elaborata correttamente
                                    self.assertEqual(response.status_code, 200)

                                    # Verifica che lo stato "uploaded" sia presente nella risposta
                                    self.assertIn(b'uploaded', response.data)

                                    # Verifica che lo stato "compiled" sia presente nella risposta
                                    self.assertIn(b'compiled', response.data)

                                    # Verifica che lo stato "execution ok" sia presente nella risposta
                                    self.assertIn(b'execution ok', response.data)

                                    # Verifica che lo stato "no output.bin" sia presente nella risposta
                                    self.assertIn(b'no output.bin', response.data)

                                    # Verifica che il numero di test superati sia 0
                                    self.assertIn(b'0 test passed', response.data)
#Caso 3: 1.upload (file main.c, senza errori di compilazione e con creazione file output.bin qualunque), 3.test, 4.check (verificando che il file  è build,  exec, output ma non test)


    def test_upload_build_exec_no_output_test(self):
        with self.app:   
            with app.app_context():  
                TestUserRoute.deleteUserfromSession()
                #TestUserRoute.test_login_con_credenziali_valide(self)
                TestUserRoute.setUp(self)   
                         
                hashed_pw = generate_password_hash('ritapolitelli',"sha256")
                user = Users(email='ritapolitelli@gmail.com', password=hashed_pw)
                # self.assertTrue(current_user.is_authenticated)
                db.session.add(user)
                db.session.commit()

                app.config['WTF_CSRF_ENABLED']=False
                # Simuliamo una richiesta POST con dati corretti
                with self.app as client:
                    response = client.post('/', data={
                        'email': 'ritapolitelli@gmail.com',
                        'password': 'ritapolitelli',
                        'remember_me': False
                    })
                
                    
                        # Imposta lo stato della sessione per l'esercizio
                #with client.session_transaction() as sess:   
                    #session['language'] = 'c'
                    #session['username'] = 'testuser'

                    # Simula l'upload di un file main.c senza errori di compilazione
                    test_file_path = 'main.c'
                    file_content = """
                                #include <stdio.h>

                                int main() {
                                printf("Hello, World!");
                                return 0;
                                }
                                """
                    with open(test_file_path, 'w') as test_file:
                                        test_file.write(file_content)

                                        # Simula la sessione per includere le chiavi necessarie
                                        with self.app.session_transaction() as session:
                                            session['exercise'] = 'esercizio_1'  # Imposta il valore desiderato per 'exercise'
                                            

                                            # Effettua la richiesta POST alla route di upload
                                            response = self.app.post('/upload', data={
                                            'file': (open(test_file_path, 'rb'), 'main.c')
                                            }, content_type='multipart/form-data', follow_redirects=True)
                                    
                            
                                            # Esegui una richiesta GET alla route '/test'
                                            response = client.get('/test', follow_redirects=True)
                                            # Verifica che la risposta sia stata elaborata correttamente
                                            self.assertEqual(response.status_code, 200)                          
                                            
                                            # Esegui una richiesta GET alla route '/checks'
                                            response = client.get('/checks', follow_redirects=True)
                                            # Verifica che la risposta sia stata elaborata correttamente
                                            self.assertEqual(response.status_code, 200)
                                            # Verifica che lo stato "uploaded" sia presente nella risposta
                                            self.assertIn(b'uploaded', response.data)
                                            # Verifica che lo stato "compiled" sia presente nella risposta
                                            self.assertIn(b'compiled', response.data)
                                            # Verifica che lo stato "execution ok" sia presente nella risposta
                                            self.assertIn(b'execution ok', response.data)
                                            # Verifica che lo stato "output.bin" sia presente nella risposta
                                            self.assertIn(b'output.bin', response.data)
                                            # Verifica che il numero di test superati sia 0
                                            self.assertIn(b'0 test passed', response.data)
                            

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUserRoute)
    testResult = unittest.TextTestRunner(verbosity=2).run(suite)

#if __name__ == '__main__':    
       # unittest.main()