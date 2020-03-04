import os
from partner import app, db, basedir
import datetime
import json
from partner.models import Instructor

class TestInstructorAPI:

    # called once at beginning of suite to create an empty db.
    @classmethod
    def setup_class(cls):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
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
        email = 'goober@email.com'
        pw = 'secret'
        response = self.app.post('/rest/instructor', data={'email': email, 'password':pw})
        assert 409 == response.status_code

    def test_get_exists (self):
        email = 'goober@email.com'
        response = self.app.get('/rest/instructor?email='+email)
        assert 200 == response.status_code
        json_data = response.get_json()
        assert json_data['id'] ==  1
        assert not json_data['authenticated']
        assert json_data['email'] == email

    def test_delete_non_exist (self):
        response = self.app.delete('/rest/instructor', data={'email': 'not-here'})
        assert 404 == response.status_code

    def test_delete_exist (self):
        email = 'goober@email.com'
        response = self.app.delete('/rest/instructor', data={'email': email})
        assert 200 == response.status_code

    def test_get__not_exists (self):
        email = 'goober@email.com'
        response = self.app.get('/rest/instructor?email='+email)
        assert 404 == response.status_code


