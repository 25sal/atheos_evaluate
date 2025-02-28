from flask import Flask, session, g
from app.init_db import url,  DATABASE_PASSWORD
from app import models, routes
import logging
from flask_cors import CORS
from flask_principal import Principal, Permission, RoleNeed, identity_loaded, UserNeed
from app.models.base import Users
from datetime import timedelta

logging.disable(logging.INFO)

app = Flask(__name__)
app.config['SECRET_KEY']= DATABASE_PASSWORD
app.config['SQLALCHEMY_DATABASE_URI'] = url
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

CORS(app)  # Abilita CORS per l'intera applicazione


# User Information providers
@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    g.user = Users.query.from_identity(identity)

routes.init_app(app)
models.init_app(app)
from app.models import db
with app.app_context():
    db.create_all()

def get_app():
    return app


# load the extension
principals = Principal(app)