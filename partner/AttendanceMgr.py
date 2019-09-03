from partner import models
import datetime

class AttendanceMgr:

    @staticmethod
    def is_present (status):
        return status != None and status == 'P'

    @staticmethod
    def update_attendance(roster, date, statuses):
        for i, s in enumerate(roster.students):
            status = statuses[i]
            s.status = status
            found = False
            for entry in s.attendance:
                if entry.date == date:
                    entry.value = status
                    found = True
                    break
            if not found:
                entry = models.AttendanceEntry(date=date, value=s.status)
                s.attendance.append(entry)

    @staticmethod
    def get_date_entry (student, date):
        for entry in student.attendance:
            if entry.date == date:
                return entry
        return None

    @staticmethod
    def get_present_students (roster, date):
        present_students = []
        for s in roster.students:
            entry = AttendanceMgr.get_date_entry(s, date)
            if AttendanceMgr.is_present(entry.value):
                present_students.append(s)
        return present_students

    # Adds a status to the student object by finding (or creating) an AttendanceEntry for the given date.
    @staticmethod
    def set_attendance_status (students, date):
        for student in students:
            date_entry = None
            for entry in student.attendance:
                if entry.date == date:
                    date_entry = entry
                    break
            if not date_entry:
                date_entry = models.AttendanceEntry(date=date, value='P')
                student.attendance.append(date_entry)
            student.status = date_entry.value

    @staticmethod
    def get_term_dates (start_date, end_date):
        d1 = start_date
        incr = datetime.timedelta(weeks=1)
        dates = [d1]
        d = d1
        while d < end_date:
            d = d + incr
            dates.append(d)
        return dates

    @staticmethod
    def generate_attendance (students, start_date, end_date):
        dates = AttendanceMgr.get_term_dates(start_date, end_date)
        date_strings = [d.strftime('%m/%d/%Y') for d in dates]
        out = 'Student Name, ' + ','.join(date_strings) + '\n'
        for student in students:
            row = student.first_name + ' ' + student.last_name
            for d in dates:
                e = AttendanceMgr.get_student_attendance(student, d)
                if not e or e == 'P':
                    row += ','
                else:
                    row += ',' + e
            out += row + '\n'

        return out


        # return [d.strftime('%m/%d/%Y') for d in dates], rows


    @staticmethod
    def get_student_attendance (student, date):
        for entry in student.attendance:
            if entry.date == date:
                return entry.value
        return None



