from partner.models import Group,Student, Roster
from partner.GroupGenerator import GroupGenerator
class TestGroupGenerator:

    def test1 (self):
        gen = GroupGenerator.get_instance()
        s1 = Student.query.filter_by(onecard_id=991242779).first()  # apodaca
        s2 = Student.query.filter_by(onecard_id=991240585).first()  # cui
        assert True == gen.is_bad_group([s1, s2])

    def test2 (self):
        gen = GroupGenerator.get_instance()
        s1 = Student.query.filter_by(onecard_id=991242779).first()  # apodaca
        s2 = Student.query.filter_by(onecard_id=991204748).first()  # destine
        assert False == gen.is_bad_group([s1, s2])


    def test_update_to_be_processed (self):
        g1 = Group(id=1)
        s1 = Student(onecard_id=1, first_name='a')
        s2 = Student(onecard_id=2, first_name='b')
        g1.members.append(s1)
        g1.members.append(s2)
        s1 = Student(onecard_id=1,first_name='a')
        s2 = Student(onecard_id=2,first_name='b')
        s3 = Student(onecard_id=3,first_name='c')
        s4 = Student(onecard_id=4,first_name='d')
        tobeproc = [s1.onecard_id, s2.onecard_id, s3.onecard_id, s4.onecard_id]
        gen = GroupGenerator.get_instance()
        gen._update_to_be_processed(tobeproc, (s1.onecard_id, s2.onecard_id))
        assert tobeproc == [s3.onecard_id, s4.onecard_id]

    def test_gen_all_possible_groups (self):
        s1 = Student(onecard_id=1, first_name='a')
        s2 = Student(onecard_id=2, first_name='b')
        s3 = Student(onecard_id=3, first_name='c')
        s4 = Student(onecard_id=4, first_name='d')
        s5 = Student(onecard_id=5, first_name='e')
        l = [s1,s2,s3,s4,s5]
        gen = GroupGenerator.get_instance()
        a = gen._generate_all_possible_groups(l)
        assert len(a) == 10
        assert a == [(1,2),(1,3),(1,4),(1,5),(2,3),(2,4),(2,5),(3,4),(3,5),(4,5)]


    def test_is_unused (self):
        gp = (1,2)
        g1 = Group(id=1)
        g1.members.append(Student(onecard_id=1,first_name='a'))
        g1.members.append(Student(onecard_id=2,first_name='b'))
        gen = GroupGenerator.get_instance()
        a = gen._is_unused(gp, [g1])
        assert a == False
        b = gen._is_unused((3,4),[g1])
        assert b == True

    def test_is_not_processed (self):

        gen = GroupGenerator.get_instance()
        a = gen._is_not_processed((1,2),[1,3,5,7])
        assert a == False
        b = gen._is_not_processed((1,2),[3,5,7])
        assert b == False
        c = gen._is_not_processed((1, 2), [1, 3, 2, 7])
        assert c == True



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
        gen = GroupGenerator.get_instance()
        a = gen.assign_partners(l, [])
        assert len(a) == 2
        assert a == [(1,2), (3,4,5)]

        g1 = Group(id=1)
        g1.members.append(s1)
        g1.members.append(s2)
        g2 = Group(id=2)
        g2.members.append(s3)
        g2.members.append(s4)
        g2.members.append(s5)
        a = gen.assign_partners(l, [g1, g2])
        assert len(a) == 2
        assert a == [(1, 3), (2,4,5)]









