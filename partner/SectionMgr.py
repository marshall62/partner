from partner import db, util
from partner.models import Section
from partner.rosters.RosterToDb import RosterToDb
from partner.AttendanceMgr import AttendanceMgr


class SectionMgr:


    @classmethod
    def get_sections_with_roster_data (cls, sections, date):
        '''
        Given a list of sections, fill each one with its roster and attendance data for the requested date
        :param sections:
        :param date:
        :return:
        '''
        l = []
        # update the roster with the attendance for the date
        for sec in sections:
            d = sec.to_dict()
            if sec.roster:
                students = sec.roster.sorted_students()
                AttendanceMgr.set_attendance_status(students, date)
                rd = sec.roster.to_dict(students)
                d['roster'] = rd
            l.append(d)
        return l

    @classmethod
    def write_sections(cls, term, year, sections_json, files):
        '''
        POSTed sections (as json) are updated/written to db.  The section objects written are returned as JSON
        :param term:
        :param year:
        :param sections_json:  all section objects
        :param files: a list of file objects being uploaded (a sections may or may not have one)
        :return: list of JSON for the sections
        '''
        res = []
        file_index = 0
        # start dates may be in one of two formats (a) mm/dd/yy or (b)yyyy-mm-ddThh:mm:ss
        # depending on whether the start date comes from the datepicker (b) or if it
        # is being taken from the existing db setting (a)
        for i, secj in enumerate(sections_json):
            # section records with a file associated in the uploaded form in db or is newly created.
            # have a flag so that it can be extracted from the list of files.
            if secj.get('fileIncluded'):
                file = files[file_index]
                file_index += 1
            else:
                file = None
            # an id indicates it already exists in the db and so we update it
            if secj.get('id'):
                res.append(cls._update_section(secj, file))
            elif term and year:
                res.append(cls._create_section(secj, file, term, year))
        db.session.commit()
        return res

    @staticmethod
    def _update_section(secj, file):
        sec = Section.query.filter_by(id=secj.get('id')).first_or_404()
        sec.title = secj.get('short_title', sec.title)
        sec.number = secj.get('number', sec.number)
        if secj.get('start_date'):
            start_date = util.str_to_date(secj.get('start_date'))
            sec.start_date = start_date
        if secj.get('fileIncluded'):
            RosterToDb.process_roster_file_upload(file, sec)
        return sec

    @staticmethod
    def _create_section(secj, file, term, year):
        start_date = secj.get('start_date')
        if start_date:
            start_date = util.str_to_date(start_date)
        else:
            start_date = util.today()
        newsec = Section(title=secj.get('short_title', ''),
                         number=secj.get('number', 0),
                         term=term, year=year,
                         start_date=start_date)
        db.session.add(newsec)
        if secj.get('fileIncluded'):
            RosterToDb.process_roster_file_upload(file, newsec)
        return newsec
