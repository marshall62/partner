import os
from partner import app, db, basedir
import datetime
import json
from partner.models import Instructor
from partner import create_user

class TestInstructorAPI:
    # Make sure FLASK_ENV environement variable is set to testing for these tests to work
    # called once at beginning of suite to create an empty db.
    @classmethod
    def setup_class(cls):
        cls.app = app.test_client()
        db.create_all()

    def setup (self):
        pass


    def teardown_class (cls):
        db.drop_all()
        db.session.commit()


    def test_create (self):
        email = 'goober@email.com'
        pw = 'secret'
        # response = self.app.post('/rest/create-instructor',
        #                          headers={"Content-Type": "application/json"}, data=payload)
        response = self.app.post('/rest/instructor', data={'email': email, 'password':pw})
        assert 200 == response.status_code
        json_data = response.get_json()
        assert json_data['id'] ==  1
        assert not json_data['authenticated']
        assert json_data['email'] == email

    def test_create_exists (self):
        email = 'phred@email.com'
        pw = 'secret'
        inst = Instructor(email=email, password=pw.encode())
        db.session.add(inst)
        db.session.commit()
        response = self.app.post('/rest/instructor', data={'email': email, 'password':pw})
        assert 409 == response.status_code

    def test_get_exists (self):
        email = 'hammerhead@email.com'
        inst = Instructor(email=email, password='secret'.encode())
        db.session.add(inst)
        db.session.commit()
        response = self.app.get('/rest/instructor?email='+email)
        assert 200 == response.status_code
        json_data = response.get_json()
        assert json_data['id'] >= 1
        assert not json_data['authenticated']
        assert json_data['email'] == email

    def test_delete_non_exist (self):
        response = self.app.delete('/rest/instructor', data={'email': 'not-here'})
        assert 404 == response.status_code

    def test_delete_exist (self):
        email = 'blee@email.com'
        inst = Instructor(email=email, password='secret'.encode())
        db.session.add(inst)
        db.session.commit()
        response = self.app.delete('/rest/instructor', data={'email': email})
        assert 200 == response.status_code

    def test_get__not_exists (self):
        email = 'NotThere@email.com'
        response = self.app.get('/rest/instructor?email='+email)
        assert 404 == response.status_code


    def test_login_succeed (self):
        email = 'login-tester@email.com'
        pw = 'secret'
        create_user.create_instructor(email,pw)
        response = self.app.post('/rest/login-instructor', data={'email': email, 'password':pw})
        assert 200 == response.status_code

    def test_login_fail (self):
        email = 'nothere@email.com'
        pw = 'secret'
        response = self.app.post('/rest/login-instructor', data={'email': email, 'password':pw})
        assert 404 == response.status_code


