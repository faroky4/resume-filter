from enum import unique

from sqlalchemy.sql.expression import false
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func



class User(db.Model, UserMixin):
    id = db.Column(db.Integer , primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    candidates = db.relationship('Candidate')
    numOfCandidates = db.Column(db.Integer)
    

class Candidate(db.Model):
    id = db.Column(db.Integer , primary_key=True)
    name = db.Column(db.String(100))
    candiEmail = db.Column(db.String(150) , unique=False)
    phoneNum = db.Column(db.String(250))
    skills = db.Column(db.String(100000))
    collageName = db.Column(db.String(150))
    degree = db.Column(db.String(150))
    experience = db.Column(db.String(1000))
    designation = db.Column(db.String(1000))
    companyNames = db.Column(db.String(1000))
    numOfPages = db.Column(db.Integer)
    totalExp = db.Column(db.Float)
    rank = db.Column(db.Integer)
    linkToCV = db.Column(db.String(1000))
    isMatch = db.Column(db.Boolean)
    company_id = db.Column(db.Integer, db.ForeignKey('user.id'))
      