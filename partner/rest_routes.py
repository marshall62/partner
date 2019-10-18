from flask_cors import cross_origin
from flask import request, jsonify

from partner import app, util
from partner.models import Section, Group
from partner.AttendanceMgr import AttendanceMgr
from partner.GroupGenerator import GroupGenerator

# REST API endpoint to save a roster JSON.
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
    students = json.get('students')
    status_codes = [s['status'] for s in students]
    #TODO rework below to handle alterations to student names.
    names_edited = False
    num_studs = len(students)
    if names_edited:
        name_edit_flags = [request.form.get('nameEditedFlag-' + str(i)) for i in range(num_studs)]
        names = [request.form.get('name-' + str(i)) for i in range(num_studs)]
        AttendanceMgr.update_student_names(r, name_edit_flags, names)
    AttendanceMgr.update_attendance(r, date, status_codes)
    return jsonify({})


# REST API endpoint to get a roster as JSON.
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
    students = list(roster.students)
    AttendanceMgr.set_attendance_status(students, date)
    # students[0].status = 'A'
    return jsonify(sec.roster.to_dict(students))

# takes a request to generate groups for a roster.  Writes to the db and returns JSON of the groups created
# needs to be given a section id and date.
@app.route('/groups', methods=['POST'])
@cross_origin()
def post_groups ():
    json = request.get_json()
    sec_id = json.get('secId')
    dt = json.get('date')
    sec = Section.query.filter_by(id=sec_id).first_or_404()
    r = sec.roster
    date = util.parse_date(dt)
    # TODO the attendance_before_gen flag needs to be an admin setting on the section
    # Under one scenario groups are generated before taking attendance and under the second scenario
    # attendance is done first so that we don't generate groups using absent students.
    groups = GroupGenerator().create_groups(r,sec.start_date,date, attendance_before_gen=False)
    # db.session.commit()
    return jsonify([g.to_dict() for g in groups])

# Returns existing groups for the section and date
@app.route('/groups', methods=['GET'])
@cross_origin()
def get_groups ():
    sec_id = request.args.get('secId');
    dt = request.args.get('date');
    sec = Section.query.filter_by(id=sec_id).first_or_404()
    r = sec.roster
    if dt:
        date = util.parse_date(dt)
    else:
        date = util.today()
    groups = Group.query.filter_by(roster_id=r.id, date=date).all()

    # db.session.commit()
    return jsonify([g.to_dict() for g in groups])

# REST API endpoint to get all sections as JSON.
@app.route('/sections', methods=['GET'])
@cross_origin()
def sections():
    sec_id = request.args.get('secId')
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
    l = []
    # update the roster with the attendance for the date
    for sec in sections:
        d = sec.to_dict()
        students = list(sec.roster.students)
        AttendanceMgr.set_attendance_status(students, date)
        rd = sec.roster.to_dict(students)
        d['roster'] = rd
        l.append(d)
    return jsonify(l)