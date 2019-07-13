from partner.models import Roster, Student
from partner import db
import csv
import re

name_map = {"studentName": "Student Name",  "oneCardId": "ID"}

class RosterToDb:
    '''
    Read a CSV file that has no attendance info and create a roster and its students in the db.  If the class/roster already is in the db, we update the students in class
    by marking registered students as active and any student left in the roster not in the current CSV as inactive.
    '''

    def __init__ (self, lab_num, meeting_time, csv_file):
        try:
            self.roster = self.find_or_make_roster(lab_num, meeting_time)
            self.read_file(csv_file)
        except Exception as exc:
            print(exc)
            db.session.rollback()


    def find_or_make_roster (self, lab_num, meeting_time):
        r = Roster.query.filter_by(lab_num=lab_num, meeting_time=meeting_time).first()
        if not r:
            r = Roster(lab_num=lab_num, meeting_time=meeting_time)
            db.session.add(r)
            db.session.commit()
        return r



    def read_file (self, csv_file):
        # The first line of the CSV file has the headers which become the keys of a dict for each row read in
        with open(csv_file, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                student = self.get_student_from_row(row)
                self.roster.students.append(student)


    # read the student info from the line and find the student in the db from onecard id or else create a new one.
    def get_student_from_row(self, row):
        name = row[name_map["studentName"]].strip()
        id = row[name_map["oneCardId"]].strip()
        s = self.find_or_make_student(id)
        fn, ln, nn = self.parse_student_name(name)
        s.first_name=fn
        s.last_name=ln
        s.nick_name=nn
        s.class_id = None # disconnect student from previous class
        return s

    def find_or_make_student (self, onecard):
        s = Student.query.filter_by(onecard_id=id).first()
        if not s:
            s = Student(onecard_id=id)
            db.session.add(s)
        return s

    # example student_name "Lebowitz-Lockard, Hannah C. (Happy)"
    def parse_student_name (self, student_name):
        m = re.match('^(?P<lname>.*),\s*(?P<fname>\w*)(.*\((?P<nname>.*)\)|.*$)', student_name)
        fname = m.group('fname')
        lname = m.group('lname')
        nname = m.group('nname')
        return fname, lname, nname

def test ():
    RosterToDb(lab_num=1, meeting_time='mon-2', csv_file='/home/david/dev/python/partner/tests/files/simple_new_classlist.csv')

test()


