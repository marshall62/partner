from partner import app, db
from partner.partner import generateGroups
from partner import util
from flask import request, render_template, flash, redirect, url_for, Response
from partner.forms import LoginForm, AttendanceForm, AttendanceStudentForm
from partner.AttendanceMgr import AttendanceMgr
from partner.GroupGenerator import GroupGenerator
from partner.rosters.RosterToDb import RosterToDb
from partner.models import Section
# from partner.ClassMgr import ClassMgr
from partner import db
from flask import jsonify
from xlsx2csv import Xlsx2csv
from werkzeug.utils import secure_filename
import os

from partner import models

ALLOWED_EXTENSIONS = {'xlsx'}

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
    names_edited = request.form.get('namesEdited')
    dt = request.form.get('date')  # mm/dd/yyyy format
    date = util.parse_date(dt)
    r = models.Roster.query.filter_by(id=roster_id).first_or_404()
    num_studs = len(list(r.students))
    if names_edited:
        name_edit_flags = [request.form.get('nameEditedFlag-' + str(i)) for i in range(num_studs)]
        names = [request.form.get('name-' + str(i)) for i in range(num_studs)]
        AttendanceMgr.update_student_names(r, name_edit_flags, names)
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
    sec = models.Section.query.filter_by(id=r.section_id).first_or_404()
    group_generator = GroupGenerator.get_instance()
    # groups = group_generator.generate_groups(r, date)
    groups = group_generator.create_groups(r,sec.start_date,date)
    db.session.commit()
    return jsonify([g.to_dict() for g in groups])

# takes a request to get a csv spreadsheet for a roster. Returns a csv file
@app.route('/roster-csv', methods=['GET'])
def roster_csv ():
    secId = request.args.get('secId')
    if secId:
        r = models.Roster.query.filter_by(section_id=secId).first_or_404() #type: Roster
        sec = models.Section.query.filter_by(id=r.section_id).first_or_404()
    else:
        flash('Must provide secId argument.  Select a lab section')
        return redirect(url_for('roster_admin'))
        year = util.get_current_year()
        term = util.get_current_term()
        sec = models.Section.query.filter_by(year=year, term=term).first_or_404()
        r = models.Roster.query.filter_by(section_id=sec.id).first_or_404()

    csv = AttendanceMgr.generate_attendance(r.students, sec.start_date, util.today())
    filename = 'lab' + str(sec.number) + '_' + sec.title + '_' + util.today().strftime('%y%m%d' + '.csv')
    return Response(csv,
                    mimetype="text/csv",
                    headers={"Content-Disposition":
                                 "attachment;filename=" + filename})

# gets the page showing a given class roster for the date/term
@app.route('/pages/rosters', methods=['GET'])
def rosters_page():
    year = util.get_current_year()
    term = util.get_current_term()
    lab_num = request.args.get('lab_number')
    dt = request.args.get('date')  # mm/dd/yyyy format
    if not dt:
        date = util.today()
        dt = util.date_to_mdy(date)
    else:
        date = util.parse_date(dt)
        year = date.year
    sections = models.Section.query.filter_by(year=year, term=term).all()
    sec = models.Section.query.filter_by(year=year, term=term, number=lab_num).first()
    if not sec:
        # TODO set error message so that 404 indicates missing resource is the sections for term/year
        sec = models.Section.query.filter_by(year=year, term=term).first_or_404()
    r = models.Roster.query.filter_by(section_id=sec.id).first_or_404("Roster not found for lab {}.  You need to create it from spreadsheet in admin page".format(sec.number))
    students = list(r.students)
    students.sort()
    AttendanceMgr.set_attendance_status(students, date)
    groups = GroupGenerator.get_existing_groups(r, date)
    return render_template('roster.html', title='Attendance', dt=dt, section=sec, sections=sections, groups=groups,
                           roster=r, students=students, num_students=len(list(r.students)))



def process_admin_section_form (year, term, dt, request):
    nums = request.form.getlist('labNums[]')
    titles = request.form.getlist('labTitles[]')
    sections = []
    for n, t in zip(nums, titles):
        if n and t:
            s = Section.query.filter_by(year=year, term=term, number=n).first()
            if s:
                s.title = t
            else:
                s = Section(year=year, term=term, number=n, title=t)
                db.session.add(s)
            sections.append(s)
    db.session.commit()
    return render_template('admin.html', title='admin', tab='sections', term=term, dt=dt, year=year, sections=sections)


@app.route('/pages/admin', methods=['GET', 'POST'])
def roster_admin():
    tab = request.form.get('tab')
    year = request.form.get('year') or request.args.get('year')
    if not year:
        year = util.get_current_year()
    term = request.form.get('term') or request.args.get('term')
    if not term:
        term = util.get_current_term()
    section = None

    dt = request.args.get('date')  # mm/dd/yyyy format
    if not dt:
        date = util.today()
        dt = util.date_to_mdy(date)

    if request.method == 'POST':

        if tab == 'section':
            return process_admin_section_form(year, term, dt, request)
        else:
            sec_id = request.form.get('labId')
            if not sec_id:
                flash('Please select a section')
                return redirect(url_for('roster_admin', term=request.form.get('term'), year=request.form.get('year')))
            section = Section.query.filter_by(id=sec_id).first_or_404()
            section.start_date = util.mdy_to_date(request.form.get('startDate'))
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            # if file.filename == '':
            #     flash('No selected file')
            #     return redirect(request.url)
            process_roster_file_upload(file, section)
            db.session.commit()
            return redirect(url_for('roster_admin', section_id=section.id))
                #TODO alter rosters_page to take a roster as input rather than meeting_time
                # return redirect(url_for('rosters_page',meeting_time='wed1')) # show the roster page for the created roster
    else:
        sec_id = request.args.get('section_id')
        if sec_id:
            section = Section.query.filter_by(id=sec_id).first_or_404()
            dt = util.date_to_mdy(section.start_date) if section.start_date else dt
    sections = Section.query.filter_by(year=year, term=term).all()

    return render_template('admin.html', title='admin', tab='rosters', year=year, term=term, section=section, dt=dt, sections=sections)


def process_roster_file_upload(file, section):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        uploaded_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        csv_filename = filename_prefix(uploaded_filename) + '.' + 'csv'
        file.save(uploaded_filename)
        Xlsx2csv(uploaded_filename, outputencoding="utf-8").convert(csv_filename)
        rdb = RosterToDb(section.id, csv_filename)
        roster = rdb.roster


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

def filename_prefix (filename):
    return filename.rsplit('.', 1)[0]

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS