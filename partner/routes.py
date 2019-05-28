from partner import app
from flask import render_template, flash, redirect, url_for
from partner.forms import LoginForm

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
    cl = [{'student': {'fname': 'David', 'lname': 'Marshall', 'nickname': 'Davo'}
                 },
                {'student': {'fname': 'Paula', 'lname': 'Nieman'},
                 'status': 'A'
                 },
                {'student': {'fname': 'Walden', 'lname': 'Marshall'}
                 },
                {'student': {'fname': 'Jonathan', 'lname': 'Marshall'},
                 'status': 'W'
                 }
                ]
    return render_template('attendance.html', title='Attendance', the_class=cl)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)