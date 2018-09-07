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
    """ The home page for the application """
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
    """ Logs out the current user """
    logout_user()
    return redirect(url_for('login'))

@app.route('/search/rooms')
def search_rooms():
    """ Provides an API endpoint which returns a list of all rooms in JSON """

    # See if there is a query
    query = request.args.get('query')
    if query:
        # Search for the query
        rooms = [i.name for i in Room.query.filter(Room.name.like('%' + query + '%'))]
    else:
        # Respond with JSON of all organizations
        rooms = [i.name for i in Room.query.all()]

    # Return the JSON response
    return jsonify(rooms)

@app.route('/search/locations')
def search_locations():
    """ Provides an API endpoint which returns a list of all locations in JSON """

    # See if there is a query
    query = request.args.get('query')
    if query:
        # Search for the query
        locations = [i.name for i in Location.query.filter(Room.name.like('%' + query + '%'))]
    else:
        # Respond with JSON of all organizations
        locations = [i.name for i in Location.query.all()]

    # Return the JSON response
    return jsonify(locations)

@app.route('/rooms/<room_id>')
def room(room_id):
    """ Displays the info page for the specified room """
    # Verify that the Room ID was passed in the URI
    if not room_id:
        flash("Room ID not specified.")
        return redirect(url_for('index'))
    # Query for the room
    room = Room.query.get(room_id)

    # TODO -- load room images

    # Verify that the room exists
    if not room:
        flash("Room does not exist.")
        return redirect(url_for('index'))
    # Return the room info page
    return render_template('room.html', room=room)

@app.route('/location/<location_name>')
def location(location_name):
    """ Displays a listing of rooms in the specified location """
    # Verify that the Room ID was passed in the URI
    if not room_id:
        flash("Room ID not specified.")
        return redirect(url_for('index'))
    # Query for the room
    room = Room.query.get(room_id)
    # Verify that the room exists
    if not room:
        flash("Room does not exist.")
        return redirect(url_for('index'))
    # Return the room info page
    return render_template('room.html', room=room)

@app.route('/admin')
@login_required
def admin():
    """ The admin page for authenticated users """
    return render_template('admin.html')

@app.route('/admin/add/location', methods=['GET', 'POST'])
@login_required
def add_location():
    """ Form to add a new location to the DB """
    # User is requesting add location form
    if request.method == 'GET':
        # Render page to user
        return render_template('add_location.html')
    # User is submitting add location data
    else:
        # Verify that a name was passed
        name = request.form.get('name')
        if not name:
            flash("Name not specified.")
            return render_template('add_location.html')
        # Verify that the location does not already exist
        location = Location.query.filter_by(name=name).first()
        if location:
            flash("Location already exists.")
            return render_template('add_location.html')
        # Create the location
        location = Location(name)
        db.session.add(location)
        db.session.commit()
        # Notify user and render admin page
        flash("Location \'" + name "\' created successfully.")
        return redirect(url_for('admin'))

@app.route('/admin/add/room', methods=['GET', 'POST'])
@login_required
def add_room():
    """ Form to add a new room to the DB """
    # User is requesting add room form
    if request.method == 'GET':
        locations = Location.query.all()
        # Render page to user
        return render_template('add_room.html', locations=locations)
    # User is submitting add room data
    else:
        # Verify that required info was passed
        name = request.form.get('name')
        location_name = request.form.get('location')
        capacity = request.form.get('capacity')
        description = request.form.get('description')
        booking_contact = request.form.get('booking_contact')
        booking_email = request.form.get('booking_email')

        # TODO -- Upload room images

        if not name:
            flash("Name not specified.")
            return render_template('add_location.html')

        if not location_name:
            flash("Location not specified.")
            return render_template('add_location.html')

        if not capacity:
            flash("Capacity not specified.")
            return render_template('add_location.html')

        # Verify that the name is unique
        room = Room.query.filter_by(name=name).first()
        if room:
            flash("Specified location name already exists.")
            render_template('add_location.html')

        # Verify that the location exists
        location = Location.query.filter_by(name=location_name).first()
        if not location:
            flash("Specified location does not exist.")
            return render_template('add_location.html')

        # Cast capacity to int
        capacity = int(capacity)

        # Create the room
        room = Room(name, location, capacity)
        room.description = description
        room.booking_contact = booking_contact
        room.booking_email = booking_email

        # Add the room to the DB
        db.session.add(room)
        db.session.commit()
        # Notify user and render admin page
        flash("Room \'" + name "\' created successfully.")
        return redirect(url_for('admin'))

@app.route('/admin/add/user', methods=['GET','POST'])
@login_required
def add_user():
    """ Allows an admin to add users to the system """

    # User is requesting form
    if request.method == 'GET':

        # Render page to user
        return render_template('add_user.html')

    # User is submitting form data
    else:
        # Get all form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')

        # Verify that required fields have been completed
        if not first_name or not last_name or not email:
            flash("All fields are required")
            return render_template('add_user.html')

        # Create user
        user = create_user(first_name, last_name, email, password)

        # Add new user to database
        db.session.add(user)
        db.session.commit()

        # Display success message
        flash('User "' + user.first_name + ' ' + user.last_name + '" Created Successfully')

        return redirect(url_for('admin'))

@app.route('/admin/remove/user', methods=['GET','POST'])
@login_required
def remove_user():
    """ Allows an admin to remove users from the system """

    # User is requesting form
    if request.method == 'GET':

        users = User.query.all()

        # Render page to user
        return render_template('remove_user.html', users=users)

    # User is submitting form data
    else:
        # Get the user from the arguments
        email = request.args.get('email')

        # Verify that the user was specified
        if not email:
            flash("Must specify a user.")
            return render_template("remove_user.html")

        # Query for the user
        user = User.query.filter_by(email=email).first()

        # Ensure that user exists
        if not user:
            flash("User does not exist.")
            return render_template("remove_user.html")

        # Ensure that user is not deleting their own account
        if user == current_user:
            flash("Cannot delete current user account.")
            return render_template("remove_user.html")

        # Remove the user from the database
        db.session.delete(user)
        db.session.commit()

        # Dispaly success message
        flash('User "' + user.first_name + ' ' + user.last_name + '" Deleted Successfully.')

        # Redirect to settings page
        return redirect(url_for('admin'))

@app.route('/admin/remove/room', methods=['GET','POST'])
@login_required
def remove_room():
    """ Allows an admin to remove rooms from the system """

    # User is requesting form
    if request.method == 'GET':

        rooms = Room.query.all()

        # Render page to user
        return render_template('remove_room.html', rooms=rooms)

    # User is submitting form data
    else:
        # Get the room to delete from the arguments
        room_id = request.args.get('room_id')

        # Verify that the room was specified
        if not room_id:
            flash("Must specify a room.")
            return render_template("remove_room.html")

        # Query for the room
        room = Room.query.filter_by(id=room_id).first()

        # Ensure that room exists
        if not room:
            flash("Room does not exist.")
            return render_template("remove_room.html")

        # Remove the room from the database
        db.session.delete(room)
        db.session.commit()

        # Dispaly success message
        flash('Room "' + room.name + '" Deleted Successfully.')

        # Redirect to settings page
        return redirect(url_for('admin'))

@app.route('/admin/remove/location', methods=['GET','POST'])
@login_required
def remove_location():
    """ Allows an admin to remove locations and all rooms contained in that
        location from the system """

    # User is requesting form
    if request.method == 'GET':

        locations = Location.query.all()

        # Render page to user
        return render_template('remove_location.html', locations=locations)

    # User is submitting form data
    else:
        # Get the location to delete from the arguments
        location_id = request.args.get('location_id')

        # Verify that the location was specified
        if not location_id:
            flash("Must specify a location.")
            return render_template("remove_location.html")

        # Query for the location
        location = Location.query.filter_by(id=location_id).first()

        # Ensure that location exists
        if not location:
            flash("Location does not exist.")
            return render_template("remove_location.html")

        # Get all rooms contained in that location
        rooms = location.rooms

        # Delete each room in the specified location
        for room in rooms:
            db.session.delete(room)

        # Remove the location from the database
        db.session.delete(location)
        # Commit the changes to the database
        db.session.commit()

        # Dispaly success message
        flash('Location "' + location.name + '" and ' + len(rooms) +
                ' Contained Rooms Deleted Successfully.')

        # Redirect to settings page
        return redirect(url_for('admin'))

# TODO -- edit location
