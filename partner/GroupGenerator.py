import random
from partner import app
from partner.models import Group, Student
from partner.AttendanceMgr import AttendanceMgr
from partner import db

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
        for s in students:
            found = False
            for bg_s in bad_group.members:
                if bg_s.onecard_id == s.onecard_id:
                    found = True
                    break
            if not found:
                return False
        return True

    def groups_are_same2 (self, student_ids, bad_group):
        for sid in student_ids:
            found = False
            for bg_s in bad_group.members:
                if bg_s.onecard_id == sid:
                    found = True
                    break
            if not found:
                return False
        return True

    # generates all pair combinations as 2-tuples
    def _generate_all_possible_groups(self, students):
        groups = []
        k = 0
        for i, s in enumerate(students):
            for j in range(i+1, len(students)):
                k += 1
                groups.append((s.onecard_id, students[j].onecard_id))
        return groups

    def _update_to_be_processed (self, to_be_processed, grp_tuple):
        for m in grp_tuple:
            to_be_processed.remove(m)

    def _is_unused (self, grp_tuple, assigned_groups):
        for g in assigned_groups:
            if self.groups_are_same2(grp_tuple,g):
                return False
        return True

    # returns whether the members of the group tuple all remain in to_be_processed
    def _is_not_processed (self, grp_tuple, to_be_processed):
        for s in grp_tuple:
            if s not in to_be_processed:
                return False
        return True

    def _is_not_processed2 (self, grp_tuple, assignment):
        for g in assignment:
            for s in grp_tuple:
                if s in g:
                    return False
        return True

    # Go through all the possible pairings and generate pairs that have never been assigned before.
    def assign_partners(self, students, previously_assigned_groups):
        all_possible = self._generate_all_possible_groups(students) # 2-tuples of student ids
        random.shuffle(all_possible) # needed so that repeat generations for a date give different ones
        i = 0
        assignment = []
        print("Previously assigned ", previously_assigned_groups)
        remaining = [s.onecard_id for s in students]
        while i < len(all_possible) and len(assignment) < len(students)//2:
            grp_tuple = all_possible[i]
            # if the pair hasn't been assigned before and the students in the pair are not in the current assignment
            # (i.e. they both remain in the to-be-processed list) then put the group in the assignment
            c1 = self._is_unused(grp_tuple, previously_assigned_groups)
            c2 = self._is_not_processed2(grp_tuple, assignment)
            if c1 and c2:
                print("Assigning ", grp_tuple, "position ", i)
                for s in grp_tuple:
                    remaining.remove(s)
                assignment.append(grp_tuple)
            elif not c1 and not c2:
                print("Group ", grp_tuple, " previously assigned and student(s) processed")
            elif not c1:
                print ("Group ", grp_tuple, " previously assigned")
            else:
                print("Group ", grp_tuple, " student(s) processed")
            i += 1
        # if one straggler remains, put them in the last group.
        if len(remaining) == 1:
            grp_tuple = grp_tuple + (remaining[0],)
            assignment[-1] = grp_tuple
        return assignment

    def create_groups(self, roster, date):
        students = AttendanceMgr.get_present_students(roster, date)

        previously_assigned_groups = Group.query.filter_by(roster_id=roster.id).all()
        group_list = self.assign_partners(students, previously_assigned_groups) # returns a list of tuples
        group_objs = []
        for grp_tuple in group_list:
            g = Group(roster_id=roster.id)
            group_objs.append(g)
            # onecard_ids are in the grp_tuple
            for s in grp_tuple:
                stud = Student.query.filter_by(onecard_id=s).first_or_404()
                g.members.append(stud)
        # delete groups created for this date
        for g in Group.query.filter_by(roster_id=roster.id, date=date).all():
            db.session.delete(g)
        # put the date on the current assignment.  This has the effect of creating a different
        # assignment (if we keep running it for the date, it will switch back and forth btw assignments)
        for g in group_objs:
            g.date = date
        return group_objs

    @staticmethod
    def get_existing_groups (roster, date):
        return Group.query.filter_by(roster_id=roster.id, date=date).all()

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



