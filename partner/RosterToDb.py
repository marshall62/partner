from partner.models import Roster, Student
from partner import db
from xlsx2csv import Xlsx2csv
from werkzeug.utils import secure_filename
from partner import app
import os
import csv
import re
import errno

class RosterToDb:
    name_map = {"studentName": "Student Name", "oneCardId": "ID"}
    spreadsheet_headers = ['Student Name', 'ID']  # others come after these but we dont care about them
    ALLOWED_EXTENSIONS = {'xlsx'}

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
                RosterToDb.remove_all_students(self._roster)
            else:
                self._roster = Roster(section_id=section_id)
                db.session.add(self._roster)
            RosterToDb.read_file(csv_file, self._roster)
            db.session.commit()
        except Exception as exc:
            print(exc)
            db.session.rollback()

    @classmethod
    def process_roster_file_upload(cls, file, section):
        if file and cls._allowed_file(file.filename):
            filename = secure_filename(file.filename)
            uploaded_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            csv_filename = cls._filename_prefix(uploaded_filename) + '.' + 'csv'
            if not os.path.exists(os.path.dirname(csv_filename)):
                try:
                    os.makedirs(os.path.dirname(csv_filename))
                except OSError as exc: # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise
            file.save(uploaded_filename)
            Xlsx2csv(uploaded_filename, outputencoding="utf-8").convert(csv_filename)
            return cls.create_roster(section, csv_filename)

    @staticmethod
    def _filename_prefix(filename):
        return filename.rsplit('.', 1)[0]

    @staticmethod
    def _allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in RosterToDb.ALLOWED_EXTENSIONS

    @classmethod
    def create_roster (cls, section, csv_file):
        try:
            secid = section.id
            with db.session.no_autoflush:
                roster = Roster.query.filter_by(section_id=secid).first()
                if roster:
                    cls.remove_all_students(roster)
                else:
                    roster = Roster(section_id=secid)
                    db.session.add(roster)
                    section.roster = roster
                cls.read_file(csv_file, roster)
            return roster
        except Exception as exc:
            print(exc)
            db.session.rollback()

    @staticmethod
    def remove_all_students (roster):
        for student in roster.students:
            roster.students.remove(student)


     # TODO skip the junk at the beginning and get to the row of headers.
    @classmethod
    def read_file (cls, csv_file, roster):
        # The first n lines of the csv file are junk and we need to skip until we see the lines following "Summary Class List"
        # following this will be a row of headers and then the data rows.
        with open(csv_file, newline='') as csvfile:
            reader = csv.DictReader(csvfile, RosterToDb.spreadsheet_headers)
            while True:
                line = next(csvfile)
                if line.startswith('Student Name'):
                    break

            for row in reader:
                student = cls.get_student_from_row(row)
                student.class_id = roster.id
                roster.students.append(student)


    # read the student info from the line and find the student in the db from onecard id or else create a new one.
    @classmethod
    def get_student_from_row(cls, row):
        name = row[RosterToDb.name_map["studentName"]].strip()
        id = row[RosterToDb.name_map["oneCardId"]].strip()
        s, found = cls.find_or_make_student(id)
        # only set name for student that didn't exist in db.
        if s and not found:
            fn, ln, nn = cls.parse_student_name(name)
            s.first_name=fn
            s.last_name=ln
            s.nick_name=nn
        return s

    @staticmethod
    def find_or_make_student (onecard):
        found = True
        s = Student.query.filter_by(onecard_id=onecard).first()
        if not s:
            found = False
            s = Student(onecard_id=onecard)
            db.session.add(s)
        return s, found

    # example student_name "Lebowitz-Lockard, Hannah C. (Happy)"
    @staticmethod
    def parse_student_name (student_name):
        m = re.match('^(?P<lname>.*),\s*(?P<fname>\w*)(.*\((?P<nname>.*)\)|.*$)', student_name)
        fname = m.group('fname')
        lname = m.group('lname')
        nname = m.group('nname')
        return fname, lname, nname