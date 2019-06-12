from partner import app
from partner.partner import Person
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
    cl_id = request.args.get('classId')
    dt = request.args.get('date') # yymmdd format
    yy = dt[0:2]
    mm = dt[2:4]
    dd = dt[4:]
    dt = mm + '/' + dd + '/' + yy
    cm = ClassMgr()
    cm.get_class(cl_id, dt)
    if request.method == 'POST':
        num_studs = int(request.form.get('numStudents'))
        statuses = [request.form.get('status-'+str(i)) for i in range(num_studs)]
        cm.update_attendance(statuses)
        cm.write_file(cl_id,dt)
    class_list = [s.to_dict() for s in cm.students]
    form = AttendanceForm()
    return render_template('attendance2.html', title='Attendance', dt=dt, form=form, class_list=class_list, num_students=len(class_list))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)