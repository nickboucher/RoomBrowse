#
# helpers.py
# Nicholas Boucher 2018
#
# Contains a set of general functions that assist the main
# application in data-processing. Also contain the login
# class.
#

from application import app
from os import urandom, makedirs
from os.path import join, isdir, dirname
from hashlib import pbkdf2_hmac
from binascii import hexlify
from models import *

def install_secret_key(app, filename='secret.key'):
    """ Configure the SECRET_KEY from a file in the
    instance directory. If the file does not exist,
    generate a random key, and save it. """
    filename = join(app.instance_path, filename)
    try:
        app.config['SECRET_KEY'] = open(filename, 'rb').read()
    except IOError:
        if not isdir(dirname(filename)):
            makedirs(dirname(filename))
        with open(filename, 'wb+') as f:
            f.write(urandom(24))
        print("Generated Random Secret Key")

def encrypt(password, salt):
    """ Provides a default implementation of the encryption algorithm used by nova """
    return hexlify(pbkdf2_hmac('sha256', str.encode(password), str.encode(salt), 100000)).decode('utf-8')

def verify_password(user, password):
    """ Checks whether the password is correct for a given user """
    return user.pw_hash == encrypt(password, user.salt)

def create_user(email, password):
    """ Handy function to create a new user """

    # Generate a random 32-byte salt
    salt = hexlify(urandom(32)).decode('utf-8')
    # Hash the password
    pw_hash = encrypt(password, salt)

    # Create the new User object
    return User(email, pw_hash, salt)
