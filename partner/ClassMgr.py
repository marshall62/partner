import csv
import os
from partner.partner import MissingDateHeaderException
from partner.Person import Person

class ClassMgr:
    name_map = {"first": "First name", "nick": "Nick name", "last": "Last name", "id": "ID number"}
    folder = "rosters/"
    lab_to_file = {1: "lab4_w1.csv", 2: "lab1_w3.csv", 3: "lab3_th1.csv", 4: "lab2_th3.csv"}
    meeting_time_to_lab_id = {'wed1': 1, 'wed3': 2, 'thurs1': 3, 'thurs3': 4}

    def __init__ (self):
        self.students = []

    def get_csv_path (self, lab_num):
        return ClassMgr.folder + ClassMgr.lab_to_file[lab_num]

    def get_lab_id (self, meeting_time):
        return self.meeting_time_to_lab_id[meeting_time]

    def get_class (self, lab_num, date):
        lab_num = int(lab_num)

        self.students = self.read_file(self.get_csv_path(lab_num), date)
        return self.students

    # get the various cells that contain the person and return it
    def get_person_from_row(self, row):
        fn = row[ClassMgr.name_map["first"]].strip()
        ln = row[ClassMgr.name_map["last"]].strip()
        nn = row[ClassMgr.name_map["nick"]].strip()
        if nn == '':
            nn = None
        id = row[ClassMgr.name_map["id"]].strip()
        return Person(fn, ln, nn, id)

    #  Return a list of students.
    def read_file(self, f, date):
        students = []

        mdyyyy =  date.strftime('%m/%d/%Y')
        mdyy =  date.strftime('%m/%d/%y')
        # The first line of the CSV file has the headers which become the keys of a dict for each row read in
        with open(f, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            headers = reader.fieldnames
            if mdyyyy in headers:
                dt_key = mdyyyy
            elif mdyy in headers:
                dt_key = mdyy
            else:
                dt_key = None
            for row in reader:
                person = self.get_person_from_row(row)
                if dt_key:
                    abs = self.get_row_absence(row, dt_key)
                    person.status = None if abs == '' else abs
                students.append(person)
        return students

    # write out the CSV file with statuses for the given date.
    def write_file (self, lab_num, date):
        path = self.get_csv_path(int(lab_num))
        mdy = date.strftime("%m/%d/%Y")
        with open(path+"tmp", 'w', newline='') as outcsvfile:
            students = iter(list(self.students))
            with open(path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                fieldnames = reader.fieldnames
                fieldnames = fieldnames if mdy in fieldnames else fieldnames + [mdy]
                writer = csv.DictWriter(outcsvfile, fieldnames=fieldnames)
                writer.writeheader()
                for row in reader:
                    s = next(students)
                    row[mdy] = s.status
                    writer.writerow(row)
        os.remove(path)
        os.rename(path+"tmp", path)


    def get_row_absence(self, row, d_yy):

        if type(row.get(d_yy, False)) == str:
            val = row[d_yy]
        else:
            raise MissingDateHeaderException(
                "Cannot find the date "  + d_yy + " at the top of the file")
        return val.strip().upper()

    def update_attendance (self, statuses):
        for i, s in enumerate(self.students):
            status = statuses[i]
            s.status = status if status else None



    def load_roster_to_db (self, filename):
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            headers = reader.fieldnames
            students = []
            for row in reader:
                person = self.get_person_from_row(row)
                students.append(person)

