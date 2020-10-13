from datetime import datetime
from partner import db
from partner import app
from partner import util
from partner import login_manager


class Section(db.Model):
    tablename__ = 'section'
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, index=True)
    term = db.Column(db.String(12), index=True)
    number = db.Column(db.Integer, index=True)
    title = db.Column(db.String(12), index=True)
    start_date = db.Column(db.Date)
    roster = db.relationship("Roster", uselist=False, back_populates="section")

    def to_dict (self):
        d = {}
        d['title'] = self.full_title
        d['short_title'] = self.title
        d['id'] = self.id
        d['number'] = self.number
        d['start_date'] = util.date_to_mdy(self.start_date)
        d['year'] = self.year
        d['term'] = self.term
        return d


    @property
    def full_title (self):
        return "Lab {}: {}".format(self.number, self.title)

    def __repr__ (self):
        return "<Section {} number:{} year:{} term:{} title:{}>".format(self.id,self.number,
        self.year, self.term, self.title)

class Roster(db.Model):
    tablename__ = 'roster'
    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'))
    section = db.relationship("Section", back_populates="roster")
    students = db.relationship('Student', backref='student', lazy='dynamic')

    def to_dict (self, students=None):
        d = {
            'lab_num': self.section.number,
            'section_id': self.section_id,
            'year': self.section.year,
            'title': self.section.full_title,
            'term': self.section.term,
            'students': [s.to_dict() for s in (self.students if not students else students)]
        }
        return d

    def sorted_students (self):
        l = list(self.students)
        l.sort()
        return l

    def __repr__(self):
        return '{} <Lab-{} {} {} {}>'.format(self.id, self.section.number, self.section.year, self.term, self.section.title)

group2student = db.Table('group2student',
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True),
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True)
)

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roster_id = db.Column(db.Integer, db.ForeignKey('roster.id'))
    date = db.Column(db.Date)
    members = db.relationship('Student', secondary=group2student, lazy='subquery',
                    backref=db.backref('groups', lazy=True))

    def to_dict(self):
        return {'id': self.id,
                'roster_id': self.roster_id,
                'date': self.date,
                'members': [s.to_dict() for s in self.members]}

    def __eq__ (self, other):
        return self.id == other.id

    def __repr__ (self):
        mems = ""
        for s in self.members:
            mems += s.__repr__() + ","
        return "<Group {} {} >".format(self.id, mems[:-1])

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    onecard_id = db.Column(db.String(12), index=True, unique=True)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    nick_name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    attendance = db.relationship('AttendanceEntry', backref='attendance', lazy='dynamic')
    class_id = db.Column(db.Integer, db.ForeignKey('roster.id'))
    status = ''

    def __lt__ (self, other):
        return self.last_name < other.last_name


    @property
    def pic_url (self):
        url = ''
        if self.onecard_id:
            url = "https://www.smith.edu/load.php?pic=" + self.onecard_id
        return url

    @property
    def preferred_fname (self):
        if self.nick_name:
            return self.nick_name
        else:
            return self.first_name

    def to_dict (self):
        return {
            'id': self.id,
            'onecard_id': self.onecard_id,
            'pic_url': self.pic_url,
            'full_name': self.preferred_fname + ' ' + self.last_name,
            'preferred_fname': self.preferred_fname,
            'first_name': self.first_name,
            'nick_name': self.nick_name,
            'last_name': self.last_name,
            'status': self.status
        }

    def __repr__(self):
        return '<{} {} {} {} {} class:{}>'.format(self.id, self.onecard_id, self.first_name, self.nick_name, self.last_name, self.class_id)


class AttendanceEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    date = db.Column(db.Date, index=True)
    value = db.Column(db.String(12), default='P')
    stud_id = db.Column(db.Integer, db.ForeignKey('student.id'))

    def __repr__(self):
        return '<Entry {} {}>'.format(self.date, self.value)




class Instructor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), index=True)
    password = db.Column(db.LargeBinary)
    authenticated = db.Column(db.Boolean, default=False)

    def is_active(self):
        return True

    def get_id (self):
        return self.id

    def get_email(self):
        return self.email

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False

    def __repr__ (self):
        return f"{self.id} {self.email} authenticated:{self.authenticated}"

    def to_dict (self):
        return { 'id': self.id, 'email': self.email, 'authenticated': self.authenticated}

@login_manager.user_loader
def user_loader(user_id):
    """Given *user_id*, return the associated User object.

    :param unicode user_id: user_id (email) user to retrieve

    """
    app.logger.debug(f"Loading user with id {user_id}")
    u = Instructor.query.get(user_id)
    app.logger.debug(f"User found {u}")
    return u