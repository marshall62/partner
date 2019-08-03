from partner import app, db
from partner.partner import generateGroups
from partner import util
from flask import request, render_template, flash, redirect, url_for
from partner.forms import LoginForm, AttendanceForm, AttendanceStudentForm
from partner.AttendanceMgr import AttendanceMgr
from partner.GroupGenerator import GroupGenerator
from partner.ClassMgr import ClassMgr
from flask import jsonify

from partner import models

# URL for testing: localhost:5000/pages/rosters

# a simple page that says hello
@app.route('/hello')
def hello():
    return 'Hello, Walden!'

@app.route('/index')
def index():
    user = {'username': 'Blee'}
    return render_template('index.html', title='Home', user=user)

# REST service endpoint to get a roster as JSON.
@app.route('/rosters', methods=['GET'])
def rosters():
    year = request.args.get('year')
    term = request.args.get('term')
    meeting_time = request.args.get('meetingTime')
    r = models.Roster.query.filter_by(year=year, term=term, meeting_time=meeting_time).first_or_404()
    return jsonify(r.to_dict())

# REST service endpoint writes the attendance to the db
@app.route('/roster-attendance', methods=['POST'])
def roster_attendance ():
    roster_id = request.form.get('rosterId')
    dt = request.form.get('date')  # mm/dd/yyyy format
    date = util.parse_date(dt)
    r = models.Roster.query.filter_by(id=roster_id).first_or_404()
    num_studs = len(list(r.students))
    statuses = [request.form.get('status-' + str(i)) for i in range(num_studs)]
    AttendanceMgr.update_attendance(r, date, statuses)
    db.session.commit()
    return jsonify({})

# takes a request to generate groups for a roster.  Writes to the db and returns JSON of the groups created
@app.route('/roster-groups', methods=['POST'])
def roster_groups ():
    roster_id = request.form.get('rosterId')
    dt = request.form.get('date')  # mm/dd/yyyy format
    date = util.parse_date(dt)
    r = models.Roster.query.filter_by(id=roster_id).first_or_404()
    group_generator = GroupGenerator.get_instance()
    groups = group_generator.generate_groups(r, date)
    db.session.commit()
    return jsonify([g.to_dict() for g in groups])

# gets the page showing a given class roster for the date/term
@app.route('/pages/rosters', methods=['GET'])
def rosters_page():
    year = util.get_current_year()
    term = util.get_current_term()
    meeting_time = request.args.get('meeting_time')
    dt = request.args.get('date')  # mm/dd/yyyy format
    if not meeting_time:
        meeting_time = 'wed1'
    if not dt:
        date = util.today()
        dt = util.to_mdy(date)
    else:
        date = util.parse_date(dt)
    r = models.Roster.query.filter_by(year=year, term=term, meeting_time=meeting_time).first_or_404()
    students = list(r.students)
    AttendanceMgr.set_attendance_status(students, date)
    return render_template('roster.html', title='Attendance', dt=dt, meeting_time=meeting_time, groups=None,
                           roster=r, students=students, num_students=len(list(r.students)))

@app.route('/test')
def test ():
    return render_template('temp.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)