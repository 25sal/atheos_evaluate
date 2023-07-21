from flask import Flask, session
from app.init_db import url,  DATABASE_PASSWORD
from app import models, routes
import logging
from flask_cors import CORS
logging.disable(logging.INFO)

app = Flask(__name__)
app.config['SECRET_KEY']= DATABASE_PASSWORD
app.config['SQLALCHEMY_DATABASE_URI'] = url
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

CORS(app)  # Abilita CORS per l'intera applicazione



routes.init_app(app)
models.init_app(app)
from app.models import db
with app.app_context():
    db.create_all()

def get_app():
    return app