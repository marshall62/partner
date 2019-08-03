from partner import models

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

