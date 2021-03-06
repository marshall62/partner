
from partner import app, db
import datetime
import json
import partner
from partner import util
from partner.models import Section, Student, Roster, AttendanceEntry

class TestSectionsAPI:
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
        response = self.app.get('/rest/sections')
        assert 200 == response.status_code
        json_data = response.get_json()
        print(json_data)

    def test_default_all_system (self):
        today = util.today()
        y = today.year
        term = util.get_term(today)
        sec = Section(year=y,term=term,number=1, start_date=util.today())
        sec2 = Section(year=y,term=term,number=2, start_date=util.today())
        sec3 = Section(year=2019,term=term,number=3, start_date=util.today())
        partner.db.session.add(sec)
        partner.db.session.add(sec2)
        partner.db.session.add(sec3)
        partner.db.session.commit()
        response = self.app.get('/rest/sections')
        assert 200 == response.status_code
        json_data = response.get_json()
        assert 2 == len(json_data)
        s1 = json_data[0]
        s2 = json_data[1]
        assert s1['number'] == sec.number
        assert s1['year'] == sec.year
        assert s1['term'] == sec.term
        assert s1['start_date'] == util.date_to_mdy(sec.start_date)
        assert s2['number'] == sec2.number
        assert s2['year'] == sec2.year
        assert s2['term'] == sec2.term
        assert s2['start_date'] == util.date_to_mdy(sec2.start_date)

    def test_get_by_id (self):
        sec = Section(year=2020,term='spring',number=1, start_date=util.today())
        sec2 = Section(year=2019,term='fall',number=2, start_date=util.today())
        partner.db.session.add(sec)
        partner.db.session.add(sec2)
        partner.db.session.commit()
        id = sec.id
        # lookup by id does not use default term or year
        response = self.app.get(f'/rest/sections?id={id}')
        assert 200 == response.status_code
        json_data = response.get_json()
        assert 1 == len(json_data)
        s1 = json_data[0]
        assert s1['number'] == sec.number
        assert s1['year'] == sec.year
        assert s1['term'] == sec.term
        assert s1['start_date'] == util.date_to_mdy(sec.start_date)

    def test_get_by_year (self):
        today = util.today()
        y = today.year
        term = util.get_term(today)
        sec = Section(year=y,term=term,number=1, start_date=today)
        sec2 = Section(year=2019,term='fall',number=2, start_date=util.today())
        partner.db.session.add(sec)
        partner.db.session.add(sec2)
        partner.db.session.commit()
        yr = sec.year
        # today's month will be used to figure out a term for default in lookup
        response = self.app.get(f'/rest/sections?year{yr}')
        assert 200 == response.status_code
        json_data = response.get_json()
        # its no longer 2019 so we should only get back one section for today's year
        assert 1 == len(json_data)
        s1 = json_data[0]
        assert s1['number'] == sec.number
        assert s1['year'] == sec.year
        assert s1['term'] == sec.term
        assert s1['start_date'] == util.date_to_mdy(sec.start_date)

    def test_get_by_term (self):
        today = util.today()
        y = today.year
        sec = Section(year=y,term='spring',number=1, start_date=today)
        sec2 = Section(year=2019,term='fall',number=2, start_date=util.today())
        partner.db.session.add(sec)
        partner.db.session.add(sec2)
        partner.db.session.commit()
        t = sec.term
        response = self.app.get(f'/rest/sections?term={t}')
        assert 200 == response.status_code
        json_data = response.get_json()
        assert 1 == len(json_data)
        s1 = json_data[0]
        assert s1['number'] == sec.number
        assert s1['year'] == sec.year
        assert s1['term'] == sec.term
        assert s1['start_date'] == util.date_to_mdy(sec.start_date)

