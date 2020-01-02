import random
from partner import app
from partner.models import Group, Student
from partner.AttendanceMgr import AttendanceMgr
from partner import db
from sqlalchemy import and_

class GroupGenerator:
    GROUP_SIZE = 2

    def __init__ (self):
        pass

    # generates all pair combinations [[x,y],...]
    def _generate_all_possible_groups(self, student_ids):
        groups = []
        k = 0
        for i, s in enumerate(student_ids):
            for j in range(i+1, len(student_ids)):
                k += 1
                groups.append([s, student_ids[j]])
        return groups


    def is_new_pair (self, pair, prev, assigned):
        for s in pair:
            if assigned.get(s):
                return False
        return pair not in prev

    def assign (self, g, assigned):
        for s in g:
            assigned[s] = True

    def unassign (self, g, assigned):
        for s in g:
            del assigned[s]

    # searches through all the possible pairs to create an arrangment of pairs such that each student is assigned to one partner
    # and that no pairing repeats a previous pairing
    # Uses backtracking similar to n-queens so that it tries to use the current (new) pair but if a full-solution can't be found,
    # it will backtrack and move to the next new pair.
    def pair_up (self, n, prev, all, res, assigned):
        # walk until a new pair is found
        for g in all:
            if self.is_new_pair(g, prev, assigned):
                self.assign(g,assigned) # mark the students in g as assigned
                res = res + [g]
                if len(res) == n:
                    return res
                # try to find a solution that includes group g
                r = self.pair_up(n, prev, all[1:], res, assigned)
                # if no solution found, unassign g's students
                if not r:
                    self.unassign(g,assigned)
                else:
                    return r
        # if we get to the end of all the pairs without finding a new one, the search fails.
        return None


    # Given a list of the student ids in the class and a list of previously assigned pairs, return an arrangement of
    # pairs that assigns each student in the class to a partner without repeating a previous pairing.
    def arrange (self, stud_ids, prev):
        random.shuffle(stud_ids)
        odd_size = False
        if len(stud_ids) % 2 != 0:
            odd_stud = stud_ids[0]
            odd_size = True
            stud_ids = stud_ids[1:]
        all = self._generate_all_possible_groups(stud_ids) # 2-tuples of student ids
        assigned = {}
        r = self.pair_up(len(stud_ids) // 2, prev, all, [], assigned)
        # if there were originally an odd number of students add the odd one in to the last group
        if odd_size:
            r[-1].append(odd_stud) # add the lone straggler to the last group
        return r


    def get_groups_csv (self, roster_id, date):
        '''
        Returns a list of CSV strings representing groups
        :param roster_id:
        :param date:
        :return:
        '''
        groups = Group.query.filter_by(roster_id=roster_id, date=date)
        rows = ""
        for g in groups:
            for m in g.members:
                rows += m.preferred_fname + ' ' + m.last_name + ','
            rows = rows[0:-1] + '\n'
        return rows

    def _get_student (self, stud_list, onecard_id):
        for s in stud_list:
            if s.onecard_id == onecard_id:
                return s
        return None

    def create_groups(self, roster, start_date, date, attendance_before_gen=True):
        if attendance_before_gen:
            students = AttendanceMgr.get_present_students(roster, date)
        # No longer works off the present students since Joe requested that I run generation BEFORE taking attendance.
        else: students = list(roster.students)
        # only find groups created for this roster since beginning of semester.
        used_groups = Group.query.filter(and_(Group.roster_id==roster.id, Group.date >= start_date)).all()
        prev_group_tuples = [[s.onecard_id for s in g.members] for g in used_groups]
        stud_ids = [s.onecard_id for s in students]
        new_group_tuples = self.arrange(stud_ids,prev_group_tuples)
        group_objs = []
        for grp_tuple in new_group_tuples:
            g = Group(roster_id=roster.id)
            group_objs.append(g)
            # onecard_ids are in the grp_tuple
            for s in grp_tuple:
                stud = self._get_student(students,s)
                g.members.append(stud)
        # delete any previously created groups for the given date and timestamp the new groups
        for g in Group.query.filter_by(roster_id=roster.id, date=date).all():
            db.session.delete(g)
        for g in group_objs:
            g.date = date

        return group_objs

    def get_existing_groups (self, roster, date):
        return Group.query.filter_by(roster_id=roster.id, date=date).all()



