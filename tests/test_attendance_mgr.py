import os
from partner import app, db, basedir
from partner.AttendanceMgr import AttendanceMgr
import datetime
from partner.models import Roster, Section, Student, AttendanceEntry

class TestAttendanceMgr:

    # called once at beginning of suite to create an empty db.
    @classmethod
    def setup_class(cls):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        cls.app = app.test_client()
        db.create_all()

    def test_term_dates (self):
        end = datetime.date(year=2019, month=8, day=10)
        start = end - datetime.timedelta(days=28)
        dates = AttendanceMgr.get_term_dates(start,end)
        assert '07/13/19' == dates[0].strftime('%m/%d/%y')
        assert '07/20/19' == dates[1].strftime('%m/%d/%y')
        assert '07/27/19' == dates[2].strftime('%m/%d/%y')
        assert '08/03/19' == dates[3].strftime('%m/%d/%y')
        assert '08/10/19' == dates[4].strftime('%m/%d/%y')


    def test_generate_attendance (self):
        end = datetime.date(year=2019, month=8, day=10)
        start = end - datetime.timedelta(days=28)
        incr = datetime.timedelta(days=7)
        s1 = Student(first_name='Chloe', last_name='Smith')
        e1 = AttendanceEntry(date=start, value='P')
        e2 = AttendanceEntry(date=start+incr, value='A')
        e3 = AttendanceEntry(date=start+incr+incr, value='P')
        s1.attendance.append(e1)
        s1.attendance.append(e2)
        s1.attendance.append(e3)

        s2 = Student(first_name='Jill', last_name='Barker')
        e2 = AttendanceEntry(date=start + incr, value='AO')
        e3 = AttendanceEntry(date=start + incr + incr, value='A')
        e4 = AttendanceEntry(date=start + incr + incr + incr, value='A')
        e5 = AttendanceEntry(date=start + incr + incr+ incr+ incr, value='AO')
        s2.attendance.append(e1)
        s2.attendance.append(e2)
        s2.attendance.append(e3)
        s2.attendance.append(e4)
        s2.attendance.append(e5)

        csv_output = AttendanceMgr.generate_attendance([s1, s2], start, end)
        lines = csv_output.split('\n')
        header = lines[0]
        header_items = header.split(',')
        assert header_items[1:] == ['07/13/2019', '07/20/2019', '07/27/2019', '08/03/2019', '08/10/2019']
        assert lines[1] == 'Chloe Smith,,A,,,'
        assert lines[2] == 'Jill Barker,,AO,A,A,AO'




