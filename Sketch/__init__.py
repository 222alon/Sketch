from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


login_manager = LoginManager()



"""Construct the core application."""
app = Flask(__name__)
db = SQLAlchemy(app)

# Configs

app.config['SECRET_KEY'] = '59348563249857213348756'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager.init_app(app)

with app.app_context():
    from . import routes  # Import routes
    db.create_all()  # Create sql tables for our data models

