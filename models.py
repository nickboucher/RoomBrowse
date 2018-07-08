#
# database_models.py
# Nicholas Boucher 2018
#
# Contains the Python Class models used to map the database to
# the application via SQLAlchemy
#

from application import app
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import UserMixin as FlaskLoginUser

# Initialize the DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# Initilize upgrade tracking
migrate = Migrate(app, db)

class User(db.Model, FlaskLoginUser):
    """ Implements a User class that can be accessed by flask-login and handled by flask-sqlalchemy """

    email = db.Column(db.Text, primary_key=True)
    pw_hash = db.Column(db.Text)
    salt = db.Column(db.Text)

    def __init__(self, email, pw_hash, salt):
        self.email = email
        self.pw_hash = pw_hash
        self.salt = salt

    def get_id(self):
        return self.email

    def __repr__(self):
        return '<User %r>' % self.email
