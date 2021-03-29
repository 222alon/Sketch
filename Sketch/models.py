from datetime import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash

from . import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):

    __tablename__ = "Users"

    id = db.Column('id', db.Integer, primary_key=True)

    username = db.Column('username', db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    # password = db.Column('password', db.String(100), nullable=False)
    created = db.Column('created', db.DateTime, index=True, default=datetime.now)

    _password_hash = db.Column('password', db.String(100), nullable=False)

    @hybrid_property
    def password(self):
        return self._password_hash

    @password.setter
    def password(self, plaintext):
        self._password_hash = generate_password_hash(plaintext)

    def validate_password(self, password):
        return check_password_hash(self._password_hash, password)

    def __repr__(self):
        return '<User: {}>'.format(self.username)

# Example of use case:
# new_user = User(username= 'alon', email = request.form['email'], password = '12345')