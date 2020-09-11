from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from . import db

"""
Form -> Model for storing data from base line csv files
Team -> Model for storing teams data
"""

class Form(db.Model):
    __tablename__ = "forms_data"
    f_id = db.Column(db.String,primary_key=True)
    date = db.Column(db.DateTime,nullable=False)
    name = db.Column(db.String,nullable=False)
    gender = db.Column(db.String,nullable=False)

class Team(db.Model):
    __tablename__ = "teams_data"
    t_id = db.Column(db.String,primary_key=True)
    name = db.Column(db.String,nullable=False)
    number = db.Column(db.Integer,nullable=False)


