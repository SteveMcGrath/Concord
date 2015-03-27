from random import SystemRandom
from hashlib import sha512, md5
from flask.ext.login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
from app.extensions import db


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)


class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'))


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    _password = db.Column(db.LargeBinary(128))
    _salt = db.Column(db.String(40))
    forgot = db.Column(db.String(32))
    roles = db.relationship('Role', secondary='user_roles', backref='users')

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        if self._salt is None:
            self._salt = bytes(SystemRandom().getrandbits(128))
        self._password = self._hash_password(value)
        self.forgot = None

    def _hash_password(self, password):
        passwd = sha512()
        passwd.update(self._salt)
        passwd.update(password.encode('utf-8'))
        return passwd.hexdigest()

    def is_valid_password(self, password):
        return self.password == self._hash_password(password)

    def forgot_password(self):
        buf = md5()
        buf.update(bytes(SystemRandom().getrandbits(128)))
        self.forgot = buf.hexdigest()
    
    def has_role(self, value):  # FIXME: currently non-optimal
        if self.roles:
            for role in self.roles:
                if role.name == value:
                    return True
        return False

        
