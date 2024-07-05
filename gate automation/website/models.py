from . import db 
from sqlalchemy import func
from flask_login import UserMixin


class White_List(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    license_plate = db.Column(db.String(200), unique=True)
    owner = db.Column(db.String(200))

class Black_List(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    license_plate = db.Column(db.String(200), unique=True)
    owner = db.Column(db.String(200))

class Entries(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    license_plate = db.Column(db.String(100))
    owner = db.Column(db.String(100))
    entry = db.Column(db.DateTime(timezone=True))
    out = db.Column(db.DateTime(timezone=True))
    car_type = db.Column(db.Integer, default=1)

class Gates(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True)
    webcam1_id = db.Column(db.Integer)
    webcam2_id = db.Column(db.Integer)

class Admins(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(200))
