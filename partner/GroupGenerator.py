import random
from partner import app
from partner.models import Group, Student
from partner.AttendanceMgr import AttendanceMgr

class GroupGenerator:
    GROUP_SIZE = 2
    bad_groups = []
    instance = None

    @classmethod
    def get_instance (cls):
        if cls.instance:
            return cls.instance
        else:
            cls.instance = GroupGenerator()
            return cls.instance

    def __init__ (self):
        path = app.config['BAD_PAIRS_FILE']
        self.read_bad_groups_file(path)

    def lookup_student (self, fname, lname):
        s = Student.query.filter_by(first_name=fname, last_name=lname).first()
        if not s:
            s = Student.query.filter_by(nick_name=fname, last_name=lname).first()
        return s

    def read_bad_groups_file (self, bad_pairs_file):
        f = open(bad_pairs_file, 'r')
        bad_pairs = []
        for line in f:
            s1, s2 = line.split(',')
            f1, l1 = s1.split()
            s1 = self.lookup_student(f1,l1)
            if not s1:
                print("Unknown student in file" + f1, l1)
                continue
            f2, l2 = s2.split()
            s2 = self.lookup_student(f2,l2)
            if not s2:
                print("Unknown student in file" + f2, l2)
                continue
            gp = {s1, s2}
            bad_pairs.append(gp)
        f.close()
        self.bad_groups = bad_pairs



    def is_bad_group (self, students):
        students = set(students)
        for g in self.bad_groups:
            if g == students:
                return True
        return False


    def groups_are_same (self, students, bad_group):
        mems = [bad_group.members]
        for s in students:
            found = False
            for bg_s in bad_group.members:
                if bg_s.onecard_id == s.onecard_id:
                    found = True
                    break
            if not found:
                return False
        return True


    def generate_groups (self, roster, date):
        student_list = AttendanceMgr.get_present_students(roster, date)

        random.shuffle(student_list)

        groups = []
        for i in range(0, len(student_list), self.GROUP_SIZE):
            # if the remaining students in the list aren't enough to create a group, put in the last group
            if len(student_list[i:]) >= self.GROUP_SIZE:
                g = student_list[i:i+self.GROUP_SIZE]
                groups.append(g)
            else:
                g = student_list[i:]
                groups.append(g)
            if self.is_bad_group(g):
                return self.generate_groups(roster, date)
        group_list = []
        for g in groups:
            group = Group(roster_id=roster.id, date=date)
            for s in g:
                group.members.append(s)
            group_list.append(group)
        return group_list



