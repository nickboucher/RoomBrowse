#
# application.py
# Nicholas Boucher 2018
#
# Contains the main application code for RoomBrowse. This code maps
# all URL endpoints to FLASK functions
#

from flask import Flask, render_template, session, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, login_user, logout_user, current_user

# Initialize the Flask application
app = Flask(__name__)

# Import all helper code
from helpers import *
from models import *

# create Flask server
app = Flask(__name__)
# Add support for database migrations
migrate = Migrate(app, db)
# Set uploaded file directory
app.config['UPLOAD_FOLDER'] = join(app.instance_path, "uploads")
if not exists(app.config['UPLOAD_FOLDER']):
    makedirs(app.config['UPLOAD_FOLDER'])
# Install the secret key for secure cookies
install_secret_key(app)
# Enable authentication
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Define authentication function to lookup users
@login_manager.user_loader
def user_loader(email):
    return User.query.get(email)

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/login', methods=['GET','POST'])
def login():
    """ Allows users to login to the system """
    # User is requesting login page
    if request.method == 'GET':
        # Render page to user
        return render_template('login.html')
    # User is submitting login data
    else:
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        # Verify that email and password were submitted
        if not email or not password:
            flash("Must enter username and password", 'error')
            return render_template('login.html')
        # Query for User
        user = User.query.get(email)
        # Verify that user exists
        if not user:
            flash("Username or password incorrect")
            return redirect(url_for('login'))
        # Verify that password is correct
        if not verify_password(user, password):
            flash("Username or password incorrect")
            return redirect(url_for('login'))
        # User has successfully authenticated, log them in
        login_user(user, remember=remember)
        # Retern to Index page
        return redirect(url_for('index'))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
