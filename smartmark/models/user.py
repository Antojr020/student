from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from . import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True, nullable=False)
    email = db.Column(db.String(120), unique=True, index=True, nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student') # 'super_admin', 'admin', 'faculty', 'student', 'parent'
    full_name = db.Column(db.String(100), nullable=True)
    avatar_url = db.Column(db.String(255), nullable=True)
    is_active_account = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    student = db.relationship('Student', backref='user', uselist=False, cascade='all, delete-orphan')
    faculty = db.relationship('Faculty', backref='user', uselist=False, cascade='all, delete-orphan')
    parent_links = db.relationship('ParentStudent', backref='parent_user', foreign_keys='ParentStudent.parent_user_id', lazy='dynamic')
    audit_logs = db.relationship('AuditLog', backref='user', lazy='dynamic')

    @property
    def is_active(self):
        # Flask-Login integration
        return self.is_active_account

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, *roles):
        # super_admin can do everything admin can
        if self.role == 'super_admin' and 'admin' in roles:
            return True
        return self.role in roles

    @property
    def display_role(self):
        role_map = {
            'super_admin': 'Super Admin',
            'admin': 'College Admin',
            'faculty': 'Faculty Member',
            'student': 'Student',
            'parent': 'Parent / Guardian'
        }
        return role_map.get(self.role, self.role.capitalize())

    def __repr__(self):
        return f'<User {self.username} [{self.role}]>'
