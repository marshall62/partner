from flask_cors import cross_origin
from flask import request, jsonify, Response

from partner import app, util
# from partner.roster_admin import process_roster_file_upload
from partner.models import Section, Group, Roster
from partner.AttendanceMgr import AttendanceMgr
from partner.GroupGenerator import GroupGenerator
from partner.SectionMgr import SectionMgr

from partner import db
import json

# REST API endpoint to save a roster (student name changes + attendance) JSON.
# body must contain secId, list of students, [date mm/dd/yyyy]
@app.route('/rosters', methods=['POST'])
@cross_origin()
def rosters_post ():
    json = request.get_json()
    sec_id = json.get('secId')
    dt = json.get('date')
    sec = Section.query.filter_by(id=sec_id).first_or_404()
    r = sec.roster
    if dt:
        date = util.mdy_to_date(dt)
    else:
        date = util.today()
    students = json.get('students') # list is sorted
    status_codes = [ s['status'] for s in students ]
    name_edits = [ True if s.get('edited') else False for s in students ]
    if True in name_edits:
        names = [s['preferred_fname'] + ' ' + s['last_name'] for s in students ]
        AttendanceMgr.update_student_names2(r, name_edits, names)
    AttendanceMgr.update_attendance(r, date, status_codes)
    db.session.commit()
    return jsonify({})


# REST API endpoint to get a roster (students plus attendance data for given date) as JSON.
@app.route('/rosters', methods=['GET'])
@cross_origin()
def rosters():
    year = request.args.get('year')
    term = request.args.get('term')
    number = request.args.get('number')
    date = request.args.get('date') # an optional parameter which, if given, will include attendance data for the date
    if date:
        date = util.parse_date(date)
    else:
        date = util.today()
    if not year:
        year = date.year
    if not term:
        term = util.get_term(date)
    if not number:
        number = 1
    sec = Section.query.filter_by(year=year, term=term, number=number).first_or_404()
    roster = sec.roster
    students = roster.sorted_students()
    AttendanceMgr.set_attendance_status(students, date)
    return jsonify(sec.roster.to_dict(students))

# Process POST request to generate groups for a roster.  Writes to the db and returns JSON of the groups created
# needs to be given a section id and date.
@app.route('/groups', methods=['POST'])
@cross_origin()
def post_groups ():
    json = request.get_json()
    sec_id = json.get('secId')
    dt = json.get('date')
    # Under one scenario groups are generated before taking attendance and under the second scenario
    # attendance is done first so that we don't generate groups using absent students.
    attendance_based = json.get('basedOnAttendance')
    sec = Section.query.filter_by(id=sec_id).first_or_404()
    r = sec.roster
    date = util.parse_date(dt)
    groups = GroupGenerator().create_groups(r,sec.start_date,date, attendance_before_gen=attendance_based)
    db.session.commit()
    return jsonify([g.to_dict() for g in groups])


# API endpoint to get existing groups for the section and date
# If the format=='csv', will produce CSV file with data and return it
# otherwise
@app.route('/groups', methods=['GET'])
@cross_origin()
def get_groups ():
    sec_id = request.args.get('secId')
    dt = request.args.get('date')
    format = request.args.get('format')
    sec = Section.query.filter_by(id=sec_id).first_or_404()
    r = sec.roster
    if dt:
        date = util.parse_date(dt)
    else:
        date = util.today()
    if format=='csv':
        csv = GroupGenerator().get_groups_csv(r.id, date) # list of csv strings where each holds students in a group
        filename = 'labgroups' + str(sec.number) + '_' + sec.title + '_' + date.strftime('%y%m%d' + '.csv')
        return Response(csv,
                        mimetype="text/csv",
                        headers={"Content-Disposition":
                                     "attachment;filename=" + filename})
    else:
        groups = Group.query.filter_by(roster_id=r.id, date=date).all()
        return jsonify([g.to_dict() for g in groups])

# REST API endpoint to get all sections as JSON.
@app.route('/sections', methods=['GET'])
@cross_origin()
def sections():
    sec_id = request.args.get('id')
    year = request.args.get('year')
    term = request.args.get('term')
    date = request.args.get('date') # an optional parameter which, if given, will include attendance data for the date
    if date:
        date = util.parse_date(date)
    else:
        date = util.today()
    if not year:
        year = date.year
    if not term:
        term = util.get_term(date)
    if sec_id:
        sections = Section.query.filter_by(id=sec_id).all()
    else:
        sections = Section.query.filter_by(year=year, term=term).all()

    sections = SectionMgr.get_sections_with_roster_data(sections, date)
    return jsonify(sections)

# Admin page POST of sections json.   Will update existing sections and create new ones.
# Will return json of all the sections for term and year
@app.route('/sections', methods=['POST'])
@cross_origin()
def set_sections ():
    term = request.form.get('term')
    year = request.form.get('year')
    #term and year get a default value in PUApp.js which intializes the PUAttendance componenent with these props.
    sections = json.loads(request.form.get('sections'))
    files = request.files.getlist('files[]')
    secs = SectionMgr.write_sections(term, year, sections, files)
    return jsonify([s.to_dict() for s in secs])


# takes a request to get a csv attendance spreadsheet for a section. Returns a csv file
@app.route('/attendance-csv', methods=['GET'])
@cross_origin()
def attendance_csv ():
    secId = request.args.get('secId')
    if secId:
        r = Roster.query.filter_by(section_id=secId).first_or_404() #type: Roster
        sec = Section.query.filter_by(id=r.section_id).first_or_404()
        csv = AttendanceMgr.generate_attendance(r.sorted_students(), sec.start_date, util.today())
        filename = 'lab' + str(sec.number) + '_' + sec.title + '_' + util.today().strftime('%y%m%d' + '.csv')
        return Response(csv,
                        mimetype="text/csv",
                        headers={"Content-Disposition":
                                     "attachment;filename=" + filename})


