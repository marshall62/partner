from partner.models import Group,Student
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


