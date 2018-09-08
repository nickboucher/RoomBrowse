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

class Room(db.Model):
    """ Bookable rooms within Harvard College """
    # General Roon Info
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, unique=True)
    description = db.Column(db.Text)
    capacity = db.Column(db.Integer, nullable=False)
    # Booking contact info
    booking_contact = db.Column(db.Text) # The contact's name
    booking_email = db.Column(db.Text)
    # Images will be populated dynamically through application logic
    # by scanning through upload folders on server
    images = []
    # Location is referenced from another table
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    location = db.relationship('Location', backref='rooms', lazy=False)

    def __init__(self, name, location, capacity):
        self.name = name
        self.location = location
        self.capacity = capacity

    def __repr__(self):
        return '<Room %r>' % self.name

class Location(db.Model)
    """ Locations in which `Room`s are housed """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Location %r>' % self.name

class User(db.Model, FlaskLoginUser):
    """ Implements a User class that can be accessed by flask-login and handled
    by flask-sqlalchemy """

    email = db.Column(db.Text, primary_key=True)
    first_name = db.Column(db.Text)
    last_name = db.Column(db.Text)
    pw_hash = db.Column(db.Text)
    salt = db.Column(db.Text)

    def __init__(self, first_name, last_name, email, pw_hash, salt):
        self.first_name = first_name
        self.las_name = last_name
        self.email = email
        self.pw_hash = pw_hash
        self.salt = salt

    def get_id(self):
        return self.email

    def __repr__(self):
        return '<User %r>' % self.email
