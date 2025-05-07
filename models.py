# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class StudyGroup(db.Model):
    __tablename__ = 'study_groups'
    id = db.Column(db.Integer, primary_key=True)
    accounting_class = db.Column(db.String(100))
    preferred_time = db.Column(db.String(100))
    preferred_days = db.Column(db.String(100))
    meeting_type = db.Column(db.String(50))  # Virtual or In-person
    campus_location = db.Column(db.String(100))
    preferred_group_size = db.Column(db.String(50))
    deleted = db.Column(db.Boolean, default=False)

    users = db.relationship('User', backref='study_group', lazy=True)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    accounting_class = db.Column(db.String(100))
    preferred_time = db.Column(db.String(100))
    preferred_days = db.Column(db.String(100))
    group_size = db.Column(db.String(50))
    meeting_type = db.Column(db.String(50))
    campus = db.Column(db.String(100))

    study_group_id = db.Column(db.Integer, db.ForeignKey('study_groups.id'))
