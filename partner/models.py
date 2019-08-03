from datetime import datetime
from partner import db

class Roster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, index=True)
    lab_num = db.Column(db.Integer, index=True)
    meeting_time =  db.Column(db.String(12), index=True)
    term = db.Column(db.String(12), index=True)
    students = db.relationship('Student', backref='student', lazy='dynamic')

    def to_dict (self):
        d = {
            'lab_num': self.lab_num,
            'year': self.year,
            'meeting_time': self.meeting_time,
            'term': self.term,
            'students': [s.to_dict() for s in self.students]
        }
        return d

    def __repr__(self):
        return '<Lab-{} {} {} {}>'.format(self.lab_num, self.year, self.term, self.meeting_time)

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roster_id = db.Column(db.Integer, db.ForeignKey('roster.id'))
    date = db.Column(db.Date)
    members = db.relationship('Student', backref='member', lazy='dynamic')

    def to_dict(self):
        return {'id': self.id,
                'roster_id': self.roster_id,
                'date': self.date,
                'members': [s.to_dict() for s in self.members]}

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    onecard_id = db.Column(db.String(12), index=True, unique=True)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    nick_name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    attendance = db.relationship('AttendanceEntry', backref='attendance', lazy='dynamic')
    class_id = db.Column(db.Integer, db.ForeignKey('roster.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    status = ''

    def to_dict (self):
        return {
            'id': self.id,
            'onecard_id': self.onecard_id,
            'first_name': self.first_name,
            'nick_name': self.nick_name,
            'last_name': self.last_name
        }

    def __repr__(self):
        return '<{} {} {}>'.format(self.first_name, self.nick_name, self.last_name)


class AttendanceEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    date = db.Column(db.Date, index=True)
    value = db.Column(db.String(12), default='P')
    stud_id = db.Column(db.Integer, db.ForeignKey('student.id'))

    def __repr__(self):
        return '<Entry {} {}>'.format(self.date, self.value)


