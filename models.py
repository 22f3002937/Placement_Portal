from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import date, datetime
from enum import Enum

db= SQLAlchemy()

class DriveStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    CLOSED = "closed"

class ApplicationStatus(str, Enum):
    APPLIED = "applied"
    SHORTLISTED = "shortlisted"
    SELECTED = "selected"
    REJECTED = "rejected"

class CompanyApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Roles(str, Enum):
    ADMIN = "admin"
    COMPANY = "company"
    STUDENT = "student"

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    role = db.Column(db.String(30))
    passwd = db.Column(db.String(256), nullable = False)
    email = db.Column(db.String(90), unique=True)
    is_active = db.Column(db.Boolean, default=True)

    company_prof = db.relationship('Company', back_populates="user")
    student_prof = db.relationship("Student", back_populates="user")



class Company(db.Model):
    __tablename__ = "companies"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    company_email = db.Column(db.String(90), unique=True)
    company_name = db.Column(db.String(150))
    hr_contact = db.Column(db.String(100))
    website = db.Column(db.String(150))
    approval_status = db.Column(db.String(20), default=CompanyApprovalStatus.PENDING.value)
    is_blacklisted = db.Column(db.Boolean, default=False)

    user = db.relationship('User', back_populates="company_prof")
    drives = db.relationship('PlacementDrive', back_populates='company', cascade="all, delete-orphan")


class PlacementDrive(db.Model, UserMixin):
    __tablename__ = "placement_drives"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    job_title = db.Column(db.String(150))
    job_description = db.Column(db.Text)
    eligibility_criteria = db.Column(db.Text)
    application_deadline = db.Column(db.Date)
    status = db.Column(db.String(20), default=DriveStatus.PENDING.value)

    company = db.relationship('Company', back_populates='drives')
    applications = db.relationship("Application", back_populates="drive", cascade="all, delete-orphan")


class Application(db.Model, UserMixin):
    __tablename__ = "applications"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drives.id'))
    applied_on = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default=ApplicationStatus.APPLIED.value)

    student = db.relationship('Student', back_populates='applications')
    drive = db.relationship('PlacementDrive', back_populates="applications")

    __table_args__ = (
        db.UniqueConstraint('student_id', 'drive_id', name='uix_student_drive'),
    )

class Student(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    branch = db.Column(db.String(50))
    cgpa = db.Column(db.Float)
    graduation_year = db.Column(db.Integer)
    resume = db.Column(db.String(200))

    user = db.relationship('User', back_populates="student_prof")
    applications = db.relationship('Application', back_populates='student')





