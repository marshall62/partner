from partner.models import Roster

class Roster:

    def __init__(self):
        pass

    def get_roster (self, lab_num, meeting_time, year, semester):
        r = Roster.query.filter_by(lab_num=lab_num, meeting_time=meeting_time, year=year, semester=semester).first()
        return r

    def get_roster_by_id (self, id):
        r = Roster.query.filter_by(id=id).first()
        return r
