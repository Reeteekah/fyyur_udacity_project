import os

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://ritikachatterjee@localhost:5432/fyyur2'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.urandom(32)

