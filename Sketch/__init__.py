from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_session import Session
from datetime import timedelta
# Eventlet message handler
import eventlet
eventlet.monkey_patch()





"""Construct the core application."""
app = Flask(__name__)
db = SQLAlchemy(app)

# Configs

app.config['SECRET_KEY'] = '59348563249857213348756'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days = 3)
app.config['SESSION_PERMANENT'] = True

socketio = SocketIO(app, async_mode="eventlet", cors_allowed_origins="*", manage_session=False)

db.init_app(app)

app.config['SESSION_SQLALCHEMY'] = db

login_manager = LoginManager()
login_manager.init_app(app)

Session(app)

with app.app_context():
	from . import routes  # Import routes
	db.create_all()  # Create sql tables for our data models

