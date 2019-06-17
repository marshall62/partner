from forms import AttendanceStudentForm
class Person:

    def __init__ (self, fname, lname, nick_name=None, id=None):
        self.fname = fname
        self.lname = lname
        self.nick_name = nick_name
        self.id = id
        self.status = None

    def full_name (self):
        if self.nick_name:
            return self.nick_name + " " + self.lname
        else:
            return self.fname + " " + self.lname

    def equals (self, other):
        return self.fname.upper() == other.fname.upper() and \
               self.lname.upper() == other.lname.upper()

    def fuzzy_equals (self, other):
        if self.lname.upper() != other.lname.upper():
            return False
        if self.nick_name == other.nick_name:
            return True
        elif self.fname == other.fname:
            return True
        elif self.nick_name == other.fname:
            return True
        elif self.fname == other.nick_name:
            return True
        else:
            return False

    def is_absent (self):
        return self.status == 'A'

    def attended_other (self):
        return self.status and self.status != 'A'

    def is_present (self):
        return not (self.is_absent() or self.attended_other())

    def to_csv (self):
        return self.fname + "," + self.lname + "," + self.id

    def to_dict (self):
        f = {}
        f['fullname'] = self.full_name()
        f['status'] = self.status
        return f

    def __str__ (self):
        return (self.nick_name if self.nick_name else self.fname) + " " + self.lname

