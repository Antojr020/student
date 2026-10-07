from datetime import datetime
from . import db

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    register_no = db.Column(db.String(20), unique=True, index=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    department = db.Column(db.String(50))
    programme = db.Column(db.String(50))
    year = db.Column(db.Integer)
    semester = db.Column(db.Integer)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    profile_image = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    marks = db.relationship('Mark', backref='student', lazy='dynamic')

class Faculty(db.Model):
    __tablename__ = 'faculty'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    employee_id = db.Column(db.String(20), unique=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    department = db.Column(db.String(50))
    designation = db.Column(db.String(50))

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    subject_code = db.Column(db.String(20), unique=True)
    subject_name = db.Column(db.String(100))
    credits = db.Column(db.Integer)
    semester = db.Column(db.Integer)
    department = db.Column(db.String(50))
    subject_type = db.Column(db.String(20)) # Theory, Practical, Elective, Project
    
    marks = db.relationship('Mark', backref='subject', lazy='dynamic')

class Mark(db.Model):
    __tablename__ = 'marks'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    internal_marks = db.Column(db.Float, default=0)
    assignment_marks = db.Column(db.Float, default=0)
    practical_marks = db.Column(db.Float, default=0)
    external_marks = db.Column(db.Float, default=0)
    total_marks = db.Column(db.Float, default=0)
    grade = db.Column(db.String(2))
    grade_point = db.Column(db.Integer)
    result = db.Column(db.String(10))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(255))
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
