from partner.models import Roster, Student
from partner import db
import csv
import re
from partner import util


name_map = {"studentName": "Student Name",  "oneCardId": "ID"}
spreadsheet_headers = ['Student Name','ID'] #others come after these but we dont care about them

class RosterToDb:

    @property
    def roster (self):
        return self._roster
    '''
    Read a CSV file that has no attendance info and create a roster and its students in the db.
    If the class/roster already is in the db, remove its students and reload with the new list of students
    '''

    def __init__ (self, section_id, csv_file):
        try:
            db.session.no_autoflush
            self._roster = Roster.query.filter_by(section_id=section_id).first()
            if self._roster:
                self.remove_all_students()
            else:
                self._roster = Roster(section_id=section_id)
                db.session.add(self._roster)
            self.read_file(csv_file)
            db.session.commit()
        except Exception as exc:
            print(exc)
            db.session.rollback()

    def remove_all_students (self):
        # self.roster.students = []
        for student in self._roster.students:
            self._roster.students.remove(student)


     # TODO skip the junk at the beginning and get to the row of headers.
    def read_file (self, csv_file):
        # The first n lines of the csv file are junk and we need to skip until we see the lines following "Summary Class List"
        # following this will be a row of headers and then the data rows.
        with open(csv_file, newline='') as csvfile:
            reader = csv.DictReader(csvfile, spreadsheet_headers)
            while True:
                line = next(csvfile)
                if line.startswith('Student Name'):
                    break

            for row in reader:
                student = self.get_student_from_row(row)
                self._roster.students.append(student)


    # read the student info from the line and find the student in the db from onecard id or else create a new one.
    def get_student_from_row(self, row):
        name = row[name_map["studentName"]].strip()
        id = row[name_map["oneCardId"]].strip()
        s, found = self.find_or_make_student(id)
        # only set name for student that didn't exist in db.
        if s and not found:
            fn, ln, nn = self.parse_student_name(name)
            s.first_name=fn
            s.last_name=ln
            s.nick_name=nn
        return s

    def find_or_make_student (self, onecard):
        found = True
        s = Student.query.filter_by(onecard_id=onecard).first()
        if not s:
            found = False
            s = Student(onecard_id=onecard)
            db.session.add(s)
        return s, found

    # example student_name "Lebowitz-Lockard, Hannah C. (Happy)"
    def parse_student_name (self, student_name):
        m = re.match('^(?P<lname>.*),\s*(?P<fname>\w*)(.*\((?P<nname>.*)\)|.*$)', student_name)
        fname = m.group('fname')
        lname = m.group('lname')
        nname = m.group('nname')
        return fname, lname, nname

def test ():
    RosterToDb(lab_num=1, meeting_time='wed1',
               year=2019, semester='fall', start_date=util.mdy_to_date('05/10/2019'), csv_file='/home/david/dev/python/partner/tests/files/simple_new_classlist.csv')

#test()

