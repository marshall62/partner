from datetime import datetime
from partner import db

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    onecard_id = db.Column(db.String(12), index=True, unique=True)
    first_name = db.Column(db.String(64), index=True, unique=True)
    last_name = db.Column(db.String(64), index=True, unique=True)
    nick_name = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    attendance = db.relationship('AttendanceEntry', backref='author', lazy='dynamic')
    class_id = db.Column(db.Integer, db.ForeignKey('roster.id'))
    def __repr__(self):
        return '<{} {}>'.format(self.first_name, self.last_name)


class AttendanceEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    date = db.Column(db.Date, index=True)
    value = db.Column(db.String(12))
    stud_id = db.Column(db.Integer, db.ForeignKey('student.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


class Roster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lab_num = db.Column(db.Integer, index=True)
    meeting_time =  db.Column(db.String(12), index=True)
    students = db.relationship('Student', backref='author', lazy='dynamic')