import logging
import os

from bs4 import BeautifulSoup


from flask import  redirect, session, url_for, request

from werkzeug.security import generate_password_hash

import app
import unittest
from app import app
from app.config import Config
from app.checker import Checker
from app.models import db
from app.models import base
from app.models.base import Users, Projects, getchecks, getexercisefolder, getexercises, savechecks, savetestresult

logger = logging.getLogger()
logging.basicConfig()


class TestUserRoute(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True


    def deleteUserfromSession(self):
        db.session.query(Users).delete()

    def test_access_registration_page(self):
            # Simula una richiesta GET per accedere alla pagina di registrazione
            response = self.app.get('/register')

            # Verifica che la risposta contenga il form di registrazione
            self.assertIn(b'<form', response.data)
            self.assertIn(b'Register', response.data)
            self.assertEqual(response.status_code, 200)


    #Register - Caso Registrazione Utente non Esistente
    def test_register_no_existing_user(self):
            
            with app.app_context():
                self.deleteUserfromSession()
                user = Users(email='ritapolitelli@gmail.com', password='ritapolitelli')
                db.session.add(user)
                db.session.commit()
            

                with self.app as client:
                    
            # Simuliamo una POST request 
                    response = client.post('/register', data={
                        'email': 'ritapolitelli@gmail.com',
                        'password_hash': 'ritapolitelli',
                        'password_hash2': 'ritapolitelli',
                        'submit': True
                    })

                    # Assicuriamoci il corretto comportamento della route con un utente esistente.
                    self.assertEqual(response.status_code, 200)


    #Register - Caso Registrazione di Utente già Esistente          
    def test_register_existing_user(self):
            #Al caso precedente, aggiungiamo il controllo di "utente già esistente" 
            with app.app_context():

                self.deleteUserfromSession()
                hashed_pw = generate_password_hash('ritapolitelli', "sha256")
                user = Users(email='ritapolitelli@gmail.com', password=hashed_pw)
                #self.assertTrue(current_user.is_authenticated)
                db.session.add(user)
                db.session.commit()
            

                    
                # Simuliamo una POST request
                app.config['WTF_CSRF_ENABLED'] = False
                response = self.app.post('/register', data={
                    'email': 'ritapolitelli@gmail.com',
                    'password_hash': 'ritapolitelli',
                    'password_hash2': 'ritapolitelli',
                    'submit': True
                })

                # Assicuriamoci il corretto comportamento della route con un utente esistente.
                self.assertEqual(response.status_code, 200)
                self.assertIn(b"User already exist.", response.data)


        

    #Login - Caso Login con Credenziali Corrette    
    def test_login_con_credenziali_valide(self):
        with self.app as client:
            with app.app_context():
                self.deleteUserfromSession()
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
                assert request.path == url_for('user_bp.languageselector')
                    
                

        #Login - Caso Login con E-Mail e Password Errate
    def test_login_con_credenziali_non_valide(self):
            with app.app_context():
                self.deleteUserfromSession()
                hashed_pw = generate_password_hash('ritapolitelli', "sha256")
                user = Users(email='ritapolitelli@gmail.com', password=hashed_pw)
                # self.assertTrue(current_user.is_authenticated)
                db.session.add(user)
                db.session.commit()
                with self.app as client:
                    # Simuliamo una POST request con dati errati
                    response = client.post('/', data={
                        'email': 'invalid_email',
                        'password': 'password',
                        'remember_me': False
                    })

                    # Nessun redirect
                                
                    self.assertEqual(response.status_code, 200)
                    '''
                    soup = BeautifulSoup(response.data.decode(), 'html.parser')
                    # print(soup)
                    hidden_div = soup.find('div', text="Oops! User doesn't exist.")
                    print(hidden_div)
                    '''

        
    #Login - Caso Login con Password non Corretta
    def test_login_con_credenziali_password_invalida(self):
        with app.app_context():
            self.deleteUserfromSession()
            hashed_pw = generate_password_hash('ritapolitelli', "sha256")
            user = Users(email='ritapolitelli@gmail.com', password=hashed_pw)
            # self.assertTrue(current_user.is_authenticated)
            db.session.add(user)
            db.session.commit()
            with self.app as client:
                app.config['WTF_CSRF_ENABLED']=False
                # Simuliamo una richiesta POST con dati corretti
                response = client.post('/', data={
                    'email': 'ritapolitelli@gmail.com',
                    'password': 'ritapolitelli1',
                    'remember_me': False
                })
                
                # Controlliamo che lo status della risposta sia 200            
                self.assertEqual(response.status_code, 200)
                self.assertIn(b'Oops! Invalid password. Please try again later.', response.data)
                                        

    def test_logout_route(self):
        
        with app.app_context():  
            
                self.deleteUserfromSession()
                TestUserRoute.setUp(self)   
                         
                hashed_pw = generate_password_hash('ritapolitelli',"sha256")
                user = Users(email='ritapolitelli@gmail.com', password=hashed_pw)
                
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
      
       
                    response = client.get('/logout', follow_redirects=True)
                    self.assertIn(b'Arrivederci', response.data)
                    response = client.get(url_for('user_bp.languageselector'), follow_redirects=True)
                     # check that the path changed
                    assert request.path == url_for('user_bp.languageselector')
                    # return redirect(url_for('user_bp.index'))
            
        
                            
    '''
    def test_upload(self):
        TestUserRoute.test_login_con_credenziali_valide(self)
        self.setUp()
        with self.app:
                # Carica un file di test
                test_file_path = 'test_file.txt'
                file_content = 'Contenuto di esempio'
                with open(test_file_path, 'w') as test_file:
                    test_file.write(file_content)

                # Simula la sessione per includere le chiavi necessarie
                with self.app.session_transaction() as session:
                    session['exercise'] = 'exercise_value'  # Imposta il valore desiderato per 'exercise'

                # Effettua la richiesta POST alla route di upload
                response = self.app.post('/upload', data={
                    'file': (open(test_file_path, 'rb'), 'test_file.txt')
                }, content_type='multipart/form-data', follow_redirects=True)

                # Controlla che il caricamento sia avvenuto con successo
                self.assertEqual(response.status_code, 200)

                # Verifica che il file sia stato salvato correttamente sul server
                uploaded_file_path = test_file_path  # Imposta il percorso corretto del file caricato
                self.assertTrue(os.path.isfile(uploaded_file_path))

                # Verifica che il contenuto del file corrisponda al file di test
                with open(uploaded_file_path, 'r') as uploaded_file:
                    uploaded_file_content = uploaded_file.read()
                    self.assertEqual(uploaded_file_content, file_content)

              
    def test_checks(self):
         
        
        #with app.test_request_context('/checks'):
         with app.app_context(): 

                self.deleteUserfromSession()
                TestUserRoute.setUp(self)   
                         
                hashed_pw = generate_password_hash('ritapolitelli',"sha256")
                user = Users(email='ritapolitelli@gmail.com', password=hashed_pw)
                
                db.session.add(user)
                db.session.commit()

                app.config['WTF_CSRF_ENABLED']=False
                  
                with app.test_client() as client:
                        with client.session_transaction() as sess:
                            sess['username'] = 'a18000387'
                            sess['language'] = 'c'
                            sess['exams'] = 1
                        
                            response = self.app.get('/checks', follow_redirects=True)
                            self.assertEqual(response.status_code, 200)

                            checks = getchecks(sess['username'])
                            if checks is None:
                                checks = {}
                            else:
                                uploaded = 'uploaded' in checks
                                compiled = uploaded and 'built' in checks and checks['built'] != 0
                                execution_ok = uploaded and 'execution' in checks and checks['execution'] != 0
                                output_bin = uploaded and 'outfile' in checks and checks['outfile'] != 0
                                test_passed = uploaded and 'test' in checks and checks['test'] != 0

                            self.assertIn(b'uploaded', response.data) if uploaded else self.assertNotIn(b'uploaded', response.data)
                            self.assertIn(b'compiled', response.data) if compiled else self.assertNotIn(b'compiled', response.data)
                            self.assertIn(b'execution ok', response.data) if execution_ok else self.assertNotIn(b'execution ok', response.data)
                            self.assertIn(b'output.bin', response.data) if output_bin else self.assertNotIn(b'output.bin', response.data)
                            self.assertIn(b'test passed', response.data) if test_passed else self.assertIn(b'tests failed', response.data)

                            self.assertIsNotNone(checks)
                            self.assertIsInstance(checks, dict)

                            exercises = getexercises(sess['language'], 0)
                            self.assertIsNotNone(exercises)
                            self.assertIsInstance(exercises, list)
                            self.assertGreater(len(exercises), 0)

              
    '''
    def test_exec(self):
        with app.app_context():
           
            self.deleteUserfromSession()
            with self.app.session_transaction() as sess:
            
                sess['exams'] = 1
            hashed_pw = generate_password_hash('ritapolitelli',"sha256")
            user = Users(email='ritapolitelli@gmail.com', password=hashed_pw)
            # self.assertTrue(current_user.is_authenticated)
            db.session.add(user)
            db.session.commit()

            #add a project for user 

            project = Projects(userid = 'ritapolitelli@gmail.com', exercise = 7, description = 'test', name='test',
                            language = 'c', checked = None)
            db.session.add(project)
            db.session.commit()
    


            app.config['WTF_CSRF_ENABLED']=False
            # Simuliamo una richiesta POST con dati corretti
            response = self.app.post('/', data={
                'email': 'ritapolitelli@gmail.com',
                'password': 'ritapolitelli',
                'remember_me': False
            })

            # Controlliamo che lo status della risposta sia 200
            self.assertEqual(response.status_code, 302) 
                        
            response = self.app.get('/testgrid')
            self.assertEqual(response.status_code, 200)

            with self.app.session_transaction() as sess:
                # Verifica che la chiave "exercise" sia presente nella sessione
                self.assertIn('exercise', sess.keys())
                #self.assertIn('exercise', sess.keys())
                # Verifica se la chiave "exercise" è impostata correttamente
                self.assertEqual(sess['exercise'], 7)
            
                # Ottieni la cartella dell'esercizio


                exer_folder = getexercisefolder(sess['exercise'], 1)[0]
                
                self.assertIsNotNone(exer_folder, "Exercise folder not found.")                
                user_folder = Config.users_dir + "/" + sess["username"] + "/" + exer_folder
                ex_folder = Config.data_dir + '/exercises/' + exer_folder
                logger.debug(sess["language"], user_folder, ex_folder)

                checker = Checker(sess['username'], sess["language"], sess["exercise"])
                results = checker.check(sess["language"], user_folder, ex_folder)
             
                self.assertEqual(checker.checks['built'],1)
                self.assertEqual(checker.checks['execution'],3)
                self.assertEqual(checker.checks['outfile'],0)  
                self.assertEqual(checker.checks['test'],0) 
                db.session.delete(project)  
                db.session.commit()                
          
            
            

                




if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUserRoute)
    testResult = unittest.TextTestRunner(verbosity=2).run(suite)
