from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FormField, FieldList, DateField, validators
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class AttendanceStudentForm (FlaskForm):
    fullname = StringField()
    absent = BooleanField()
    attendedOther = BooleanField()

class AttendanceGroupForm (FlaskForm):
    members = FieldList(AttendanceStudentForm)


class AttendanceForm(FlaskForm):
    students = FieldList(FormField(AttendanceStudentForm))
    groups = FieldList(FormField(AttendanceGroupForm))
    submit = SubmitField()