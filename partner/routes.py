from partner import app
from partner.partner import generateGroups
from partner import util
from flask import request, render_template, flash, redirect, url_for
from partner.forms import LoginForm, AttendanceForm, AttendanceStudentForm
from partner.ClassMgr import ClassMgr

# a simple page that says hello
@app.route('/hello')
def hello():
    return 'Hello, Walden!'

@app.route('/index')
def index():
    user = {'username': 'Miguel'}
    return render_template('index.html', title='Home', user=user)

@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    meeting_time = request.args.get('meeting_time')
    if not meeting_time:
        meeting_time = 'wed1'
    cl_id = ClassMgr().get_lab_id(meeting_time)
    dt = request.args.get('date') # mm/dd/yyyy format
    if not dt:
        date = util.today()
        dt = util.to_mdy(date)
    else:
        date = util.parse_date(dt)
    cm = ClassMgr()
    cm.get_class(cl_id, date)
    groups = []
    #TODO figure out how to init with the partners2avoid file.
    if request.method == 'POST':
        # if generate partners button clicked, don't update attendance
        if request.form.get('gen_partners')  == 'true':
            print("gen partners")
            present_students = list(filter(lambda x: x.is_present(), cm.students))
            groups = [g.to_dict() for g in generateGroups(present_students, [])]
        else:
            num_studs = int(request.form.get('numStudents'))
            statuses = [request.form.get('status-'+str(i)) for i in range(num_studs)]
            cm.update_attendance(statuses)
            cm.write_file(cl_id, date)
    class_list = [s.to_dict() for s in cm.students]
    return render_template('attendance.html', title='Attendance', dt=dt, meeting_time=meeting_time, groups=groups, class_list=class_list, num_students=len(class_list))


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