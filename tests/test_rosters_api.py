import os
from partner import app, db, basedir, create_user
import datetime
import json
from partner.models import Section, Student, Roster, AttendanceEntry

class TestRostersAPI:
    # Make sure FLASK_ENV environement variable is set to testing for these tests to work
    # called once at beginning of suite to create an empty db.
    @classmethod
    def setup_class(cls):
        cls.app = app.test_client()
        db.create_all()


    def setup (self):
        db.create_all()

    def teardown (self):
        db.drop_all()
        db.session.commit()

    def teardown_class (cls):
        db.drop_all()
        db.session.commit()


    def test_get_none_in_system (self):
        response = self.app.get('/rest/rosters?year=2020&term=fall&number=1')
        assert 404 == response.status_code

    def test_get (self):
        y = 2020
        term='fall'
        number = 1
        roster = Roster()
        s1 = Student(first_name='f1', last_name='l1')
        roster.students.append(s1)
        sec = Section(year=y,term=term,number=number,roster=roster)
        db.session.add(s1)
        db.session.add(roster)
        db.session.add(sec)
        db.session.commit()
        response = self.app.get(f'/rest/rosters?year={y}&term={term}&number={number}')
        assert 200 == response.status_code
        json_data = response.get_json()
        assert number == json_data['lab_num']
        assert term == json_data['term']
        assert y == json_data['year']
        studs = json_data['students']
        assert studs[0]['first_name'] == 'f1'
        assert studs[0]['last_name'] == 'l1'

    def test_get_for_date (self):
        y = 2020
        term='fall'
        number = 1
        roster = Roster()
        s1 = Student(first_name='f1', last_name='l1')
        roster.students.append(s1)
        sec = Section(year=y,term=term,number=number,roster=roster)
        dt = datetime.datetime.now()
        ae = AttendanceEntry(stud_id=s1.id, date=dt,value='A')
        s1.attendance.append(ae)
        db.session.add(s1)
        db.session.add(ae)
        db.session.add(roster)
        db.session.add(sec)
        db.session.commit()
        response = self.app.get(f'/rest/rosters?year={y}&term={term}&number={number}')
        assert 200 == response.status_code
        json_data = response.get_json()
        assert number == json_data['lab_num']
        assert term == json_data['term']
        assert y == json_data['year']
        studs = json_data['students']
        assert studs[0]['first_name'] == 'f1'
        assert studs[0]['last_name'] == 'l1'
        assert studs[0]['status'] == 'A'

    def test_post_nothing (self):
        response = self.app.post('/rest/rosters')
        assert 400 == response.status_code

    def test_post_roster (self):
        y = 2020
        term='fall'
        number = 1
        roster = Roster()
        s1 = Student(first_name='f1', last_name='l1')
        s2 = Student(first_name='f2', last_name='l2')
        roster.students.append(s1)
        roster.students.append(s2)
        sec = Section(year=y,term=term,number=number,roster=roster)
        db.session.add(s1)
        db.session.add(s2)
        db.session.add(roster)
        db.session.add(sec)
        db.session.commit()
        dt = datetime.datetime.now()
        mdy = f'{dt.month}/{dt.day}/{dt.year}'
        students = [{'full_name': 'f1 l1', 'status': 'A', 'edited': True}, {'full_name': 'f2 l2', 'status': 'AO', 'edited': False}]
        response = self.app.post('/rest/rosters', json={'secId': 1, 'date': mdy, 'students': students})
        assert 200 == response.status_code

    def test_post_empty_roster (self):
        y = 2020
        term='fall'
        number = 1
        roster = Roster()
        s1 = Student(first_name='f1', last_name='l1')
        s2 = Student(first_name='f2', last_name='l2')
        roster.students.append(s1)
        roster.students.append(s2)
        sec = Section(year=y,term=term,number=number,roster=roster)
        db.session.add(s1)
        db.session.add(s2)
        db.session.add(roster)
        db.session.add(sec)
        db.session.commit()
        dt = datetime.datetime.now()
        mdy = f'{dt.month}/{dt.day}/{dt.year}'
        students = []
        response = self.app.post('/rest/rosters', json={'secId': 1, 'date': mdy, 'students': students})
        assert 200 == response.status_code

    def test_post_students_missing (self):
        y = 2020
        term='fall'
        number = 1
        roster = Roster()
        s1 = Student(first_name='f1', last_name='l1')
        s2 = Student(first_name='f2', last_name='l2')
        roster.students.append(s1)
        roster.students.append(s2)
        sec = Section(year=y,term=term,number=number,roster=roster)
        db.session.add(s1)
        db.session.add(s2)
        db.session.add(roster)
        db.session.add(sec)
        db.session.commit()
        dt = datetime.datetime.now()
        mdy = f'{dt.month}/{dt.day}/{dt.year}'
        response = self.app.post('/rest/rosters', json={'secId': 1, 'date': mdy})
        assert 200 == response.status_code
