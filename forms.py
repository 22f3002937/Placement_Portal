from flask_wtf import FlaskForm
from wtforms import SearchField, PasswordField,IntegerField, SubmitField, StringField, SelectField, TextAreaField, DateField, TimeField, FloatField
from wtforms.validators import DataRequired, Email, Length, NumberRange, URL, Optional


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators = [DataRequired()])

    submit = SubmitField("Login")

class StudentRegistrationForm(FlaskForm):
    name = StringField("Full name", validators=[DataRequired() ])
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    branch = StringField("Branch", validators=[DataRequired()])
    cgpa = FloatField("CGPA", validators=[DataRequired()])
    graduation_year = IntegerField("Graduation Year", validators=[DataRequired()])
    submit = SubmitField("Register")

class StudentUpdateForm(FlaskForm):
    name = StringField("Full name", validators=[DataRequired() ])
    # email = StringField("Email", validators=[DataRequired()])
    # password = PasswordField("Password", validators=[DataRequired()])
    branch = StringField("Branch", validators=[DataRequired()])
    cgpa = FloatField("CGPA", validators=[DataRequired()])
    graduation_year = IntegerField("Graduation Year", validators=[DataRequired()])
    submit = SubmitField("Update Profile")

class CompanyRegistrationForm(FlaskForm):
    name = StringField("Company name", validators=[DataRequired() ])
    email = StringField("Company email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    hr_contact = StringField("HR Contact", validators=[DataRequired() ])
    website = StringField("Company website", validators=[DataRequired() ])
    submit = SubmitField("Register Company")

class CompanyProfileUpdateForm(FlaskForm):

    name = StringField("Company name", validators=[DataRequired() ])
    hr_contact = StringField("HR Contact Name",validators=[DataRequired()])
    website = StringField("Company Website",validators=[Optional()])
    submit = SubmitField("Update Profile")

class PlacementDriveForm(FlaskForm):
    job_title = StringField("Job Title", validators=[DataRequired()])
    job_description = TextAreaField("Job Description", validators=[DataRequired()])
    eligibility_criteria = TextAreaField("Eligibility Criteria", validators=[DataRequired()])
    application_deadline = DateField("Application Deadline", format="%Y-%m-%d", validators=[DataRequired()])
    submit =  SubmitField("Create Drive")

class ApplicationStatusUpdateForm(FlaskForm):
    status = SelectField("Update status", choices=[("shortlisted", "Shortlisted"),
                                                ("selected","Selected"),
                                                    ("rejected","Rejected")], validators=[DataRequired()])
    submit = SubmitField("Update Status")

class AdminSearchForm(FlaskForm):
    query =StringField("Search by name/ Email/ ID", validators=[DataRequired()])    
    submit = SubmitField("Search")

    

