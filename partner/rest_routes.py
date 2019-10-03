from flask_cors import cross_origin
from flask import request, jsonify

from partner import app, util
from partner.models import Section
from partner.AttendanceMgr import AttendanceMgr

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
    print(status_codes)
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
    sec = Section.query.filter_by(year=year, term=term, number=number).first_or_404()
    roster = sec.roster
    students = list(roster.students)
    AttendanceMgr.set_attendance_status(students, date)
    students[0].status = 'A'
    return jsonify(sec.roster.to_dict(students))
