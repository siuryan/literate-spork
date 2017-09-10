from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    username = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(120), index=True, unique=False)
                         
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    admin = db.Column(db.Boolean, index=True, unique=False)

    adds = db.relationship('Add', backref='user', lazy='dynamic')
    drops = db.relationship('Drop', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % (self.nickname)

    def set_password(self, pwd):
        self.password = generate_password_hash(pwd)

    def check_password(self, pwd):
        return check_password_hash(self.password, pwd)

class Add(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    class_id = db.Column(db.Integer, db.ForeignKey('school_class.id'))

class Drop(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    class_id = db.Column(db.Integer, db.ForeignKey('school_class.id'))

class SchoolClass(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String, index=True, unique=False)

    adds = db.relationship('Add', backref='school_class', lazy='dynamic')
    drops = db.relationship('Drop', backref='school_class', lazy='dynamic')

    period = db.Column(db.Integer, index=True, unique=False)
    teacher = db.Column(db.Integer, index=True, unique=False)


    
