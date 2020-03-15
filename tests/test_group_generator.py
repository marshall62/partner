from partner.models import Group,Student, Roster, Section
from partner.GroupGenerator import GroupGenerator
import os
from partner import util
from partner import app, db, basedir

class TestGroupGenerator():
    # Make sure FLASK_ENV environement variable is set to testing for these tests to work
    # called once at beginning of suite to create an empty db.
    @classmethod
    def setup_class(cls):
        cls.app = app.test_client()
        db.create_all()

    @classmethod
    def teardown_class(cls):
        pass

    # called at the beginning of each test.
    def setup(self):
        pass

    def test_gen_all_possible_groups (self):
        l = [1,2,3,4,5]
        gen = GroupGenerator()
        a = gen._generate_all_possible_groups(l)
        assert len(a) == 10
        assert a == [[1,2],[1,3],[1,4],[1,5],[2,3],[2,4],[2,5],[3,4],[3,5],[4,5]]



    def test_gen_groups2 (self):
        r = Roster(id=1)
        s1 = Student(onecard_id=1, first_name='a')
        s2 = Student(onecard_id=2, first_name='b')
        s3 = Student(onecard_id=3, first_name='c')
        s4 = Student(onecard_id=4, first_name='d')
        s5 = Student(onecard_id=5, first_name='e')
        l = [s1,s2,s3,s4,s5]
        r.students.append(s1)
        r.students.append(s2)
        r.students.append(s3)
        r.students.append(s4)
        r.students.append(s5)
        dt = util.mdy_to_date('09/15/2019')
        start_dt = util.mdy_to_date('09/11/2019')
        gen = GroupGenerator()
        a = gen.create_groups(r,start_dt,dt, attendance_before_gen=False)
        assert len(a) == 2
        g1 = Group(id=1)
        g1.members.append(s1)
        g1.members.append(s2)
        g2 = Group(id=2)
        g2.members.append(s3)
        g2.members.append(s4)
        g2.members.append(s5)
        a = gen.create_groups(r, start_dt,dt, attendance_before_gen=False)
        assert len(a) == 2



    # @pytest.mark.skip(reason="slow test")
    def test_create_groups2 (self):
        r = Roster()
        s1 = Student(onecard_id=1, first_name='a')
        s2 = Student(onecard_id=2, first_name='b')
        s3 = Student(onecard_id=3, first_name='c')
        s4 = Student(onecard_id=4, first_name='d')
        s5 = Student(onecard_id=5, first_name='e')
        s6 = Student(onecard_id=6, first_name='f')
        l = [s1, s2, s3, s4, s5, s6]
        g1 = Group(id=1)
        g1.members.append(s1)
        g1.members.append(s2)
        g2 = Group(id=2)
        g2.members.append(s3)
        g2.members.append(s4)
        g3 = Group(id=3)
        g3.members.append(s5)
        g3.members.append(s6)
        r.students.append(s1)
        r.students.append(s2)
        r.students.append(s3)
        r.students.append(s4)
        r.students.append(s5)
        r.students.append(s6)
        gen = GroupGenerator()
        dt = util.mdy_to_date('09/15/2019')
        start_dt = util.mdy_to_date('09/11/2019')
        gps = gen.create_groups(r,start_dt,dt,attendance_before_gen=True)
        assert 3 == len(gps)


    def test_arrange1 (self):
        all_poss = [[3, 5], [4, 6], [2, 5], [1, 5], [1, 2], [5, 6], [1, 4], [2, 6], [3, 6], [3, 4], [4, 5], [1, 6], [1, 3], [2, 4], [2, 3]]
        prev = []
        gen = GroupGenerator()
        a = gen.pair_up(3, prev, all_poss,[], {})
        print(a)
        assert len(a) == 3
        assert [[3,5],[4,6],[1,2]] == a

    def test_arrange (self):
        all_poss = [[3, 5], [4, 6], [2, 5], [1, 5], [1, 2], [5, 6], [1, 4], [2, 6], [3, 6], [3, 4], [4, 5], [1, 6], [1, 3], [2, 4], [2, 3]]
        prev = [[1,2],[3,4],[5,6]]
        gen = GroupGenerator()
        a = gen.pair_up(3,prev,all_poss,[],{})
        print(a)
        assert len(a) == 3

    def test_arrange2 (self):
        prev = [[1,2,3]]
        gen = GroupGenerator()
        a = gen.arrange([1,2,3], prev)
        assert set(a[0]) == {1,2,3}

    def test_arrange3 (self):
        prev = []
        gen = GroupGenerator()
        a = gen.arrange([1,2,3],prev)
        print(a)
        assert {1,2,3} == set(a[0])







