from datetime import datetime, date
from . import db

class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, index=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    hod_name = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    courses = db.relationship('Course', backref='department_rel', lazy='dynamic')
    faculty_members = db.relationship('Faculty', backref='department_rel', lazy='dynamic')
    students = db.relationship('Student', backref='department_rel', lazy='dynamic')
    subjects = db.relationship('Subject', backref='department_rel', lazy='dynamic')

    def __repr__(self):
        return f'<Department {self.code} - {self.name}>'


class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), unique=True, index=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    degree_type = db.Column(db.String(50), default='Undergraduate') # Undergraduate, Postgraduate, Diploma
    duration_years = db.Column(db.Integer, default=4)
    total_semesters = db.Column(db.Integer, default=8)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    students = db.relationship('Student', backref='course_rel', lazy='dynamic')
    subjects = db.relationship('Subject', backref='course_rel', lazy='dynamic')

    def __repr__(self):
        return f'<Course {self.course_code} - {self.name}>'


class AcademicYear(db.Model):
    __tablename__ = 'academic_years'
    id = db.Column(db.Integer, primary_key=True)
    year_name = db.Column(db.String(20), unique=True, nullable=False) # e.g. "2025-2026"
    is_current = db.Column(db.Boolean, default=False)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    semesters = db.relationship('Semester', backref='academic_year_rel', lazy='dynamic')
    examinations = db.relationship('Examination', backref='academic_year_rel', lazy='dynamic')

    def __repr__(self):
        return f'<AcademicYear {self.year_name}>'


class Semester(db.Model):
    __tablename__ = 'semesters'
    id = db.Column(db.Integer, primary_key=True)
    semester_number = db.Column(db.Integer, nullable=False) # 1 to 8
    semester_name = db.Column(db.String(50), nullable=False) # e.g. "Semester 1 (Odd 2025)"
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_years.id'), nullable=False)
    is_current = db.Column(db.Boolean, default=False)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)

    def __repr__(self):
        return f'<Semester {self.semester_number} - {self.semester_name}>'


class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    register_no = db.Column(db.String(30), unique=True, index=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=True)
    admission_year = db.Column(db.Integer, default=2024)
    current_semester = db.Column(db.Integer, default=1)
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_years.id'), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), default='Male')
    profile_image = db.Column(db.String(255), nullable=True)
    enrollment_status = db.Column(db.String(20), default='Active') # Active, Inactive, Graduated, Suspended
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    marks = db.relationship('Mark', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    attendance_records = db.relationship('AttendanceRecord', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    parent_links = db.relationship('ParentStudent', backref='student', lazy='dynamic', cascade='all, delete-orphan')

    # Compatibility properties
    @property
    def department(self):
        if self.department_rel:
            return self.department_rel.name
        return "Computer Science & Engineering"

    @property
    def programme(self):
        if self.course_rel:
            return self.course_rel.name
        return "B.Tech"

    @property
    def semester(self):
        return self.current_semester

    @property
    def year(self):
        # Calculate year based on current semester (sem 1,2 = yr 1; 3,4 = yr 2; etc.)
        return (self.current_semester + 1) // 2

    @property
    def age(self):
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None

    def __repr__(self):
        return f'<Student {self.register_no} - {self.name}>'


class Faculty(db.Model):
    __tablename__ = 'faculty'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    employee_id = db.Column(db.String(30), unique=True, index=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    designation = db.Column(db.String(50), default='Assistant Professor') # Professor, Assoc Professor, Asst Professor, Lecturer
    qualification = db.Column(db.String(100), nullable=True)
    joining_date = db.Column(db.Date, nullable=True)
    profile_image = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Assignments
    assignments = db.relationship('FacultySubjectAssignment', backref='faculty', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def department(self):
        if self.department_rel:
            return self.department_rel.name
        return "General"

    def __repr__(self):
        return f'<Faculty {self.employee_id} - {self.name}>'


class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    subject_code = db.Column(db.String(20), unique=True, index=True, nullable=False)
    subject_name = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=True)
    semester = db.Column(db.Integer, nullable=False, default=1)
    credits = db.Column(db.Integer, nullable=False, default=3)
    subject_type = db.Column(db.String(20), default='Theory') # Theory, Practical, Elective, Project
    max_internal = db.Column(db.Float, default=40.0)
    max_external = db.Column(db.Float, default=60.0)
    max_marks = db.Column(db.Float, default=100.0)
    pass_marks = db.Column(db.Float, default=40.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    marks = db.relationship('Mark', backref='subject', lazy='dynamic')
    attendance_records = db.relationship('AttendanceRecord', backref='subject', lazy='dynamic')
    faculty_assignments = db.relationship('FacultySubjectAssignment', backref='subject', lazy='dynamic')

    @property
    def department(self):
        if self.department_rel:
            return self.department_rel.name
        return "General"

    def __repr__(self):
        return f'<Subject {self.subject_code} - {self.subject_name}>'


class FacultySubjectAssignment(db.Model):
    __tablename__ = 'faculty_subject_assignments'
    id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_years.id'), nullable=True)
    section = db.Column(db.String(10), default='A')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<FacultyAssignment Faculty:{self.faculty_id} Subject:{self.subject_id}>'


class ParentStudent(db.Model):
    __tablename__ = 'parent_students'
    id = db.Column(db.Integer, primary_key=True)
    parent_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    relationship = db.Column(db.String(50), default='Parent') # Father, Mother, Guardian
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ParentStudent Parent:{self.parent_user_id} Student:{self.student_id}>'


class ExamType(db.Model):
    __tablename__ = 'exam_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False) # 'Internal Assessment 1', 'Model Examination', 'Semester Examination'
    code = db.Column(db.String(20), unique=True, nullable=False) # 'IA-1', 'IA-2', 'MODEL', 'SEM'
    weightage_percent = db.Column(db.Float, default=20.0)
    description = db.Column(db.String(200), nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    examinations = db.relationship('Examination', backref='exam_type_rel', lazy='dynamic')

    def __repr__(self):
        return f'<ExamType {self.code} - {self.name}>'


class Examination(db.Model):
    __tablename__ = 'examinations'
    id = db.Column(db.Integer, primary_key=True)
    exam_type_id = db.Column(db.Integer, db.ForeignKey('exam_types.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_years.id'), nullable=False)
    semester = db.Column(db.Integer, nullable=False, default=1)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='Scheduled') # Scheduled, In Progress, Completed, Published
    is_published = db.Column(db.Boolean, default=False)
    published_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    marks = db.relationship('Mark', backref='examination_rel', lazy='dynamic')

    @property
    def exam_type_name(self):
        return self.exam_type_rel.name if self.exam_type_rel else "Exam"

    def __repr__(self):
        return f'<Examination {self.name} (Sem {self.semester})>'


class Mark(db.Model):
    __tablename__ = 'marks'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    examination_id = db.Column(db.Integer, db.ForeignKey('examinations.id'), nullable=True)
    
    internal_marks = db.Column(db.Float, default=0.0)
    assignment_marks = db.Column(db.Float, default=0.0)
    practical_marks = db.Column(db.Float, default=0.0)
    external_marks = db.Column(db.Float, default=0.0)
    total_marks = db.Column(db.Float, default=0.0)
    percentage = db.Column(db.Float, default=0.0)
    grade = db.Column(db.String(5), default='F')
    grade_point = db.Column(db.Integer, default=0)
    result = db.Column(db.String(10), default='PASS') # PASS, FAIL, WITHHELD
    status = db.Column(db.String(20), default='draft') # draft, submitted, approved, rejected
    
    entered_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    approved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    remarks = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    entered_by = db.relationship('User', foreign_keys=[entered_by_id])
    approved_by = db.relationship('User', foreign_keys=[approved_by_id])

    __table_args__ = (
        db.UniqueConstraint('student_id', 'subject_id', 'examination_id', name='uq_student_subject_exam'),
    )

    def calculate_results(self, pass_mark=40.0):
        int_m = float(self.internal_marks or 0.0)
        assign_m = float(self.assignment_marks or 0.0)
        prac_m = float(self.practical_marks or 0.0)
        ext_m = float(self.external_marks or 0.0)
        self.total_marks = round(int_m + assign_m + prac_m + ext_m, 2)
        max_m = float(self.subject.max_marks) if self.subject and self.subject.max_marks else 100.0
        self.percentage = round((self.total_marks / max_m) * 100, 2)
        
        # Grading Scale (10-Point Scale)
        if self.percentage >= 90:
            self.grade, self.grade_point = 'O', 10
        elif self.percentage >= 80:
            self.grade, self.grade_point = 'A+', 9
        elif self.percentage >= 70:
            self.grade, self.grade_point = 'A', 8
        elif self.percentage >= 60:
            self.grade, self.grade_point = 'B+', 7
        elif self.percentage >= 50:
            self.grade, self.grade_point = 'B', 6
        elif self.percentage >= 40:
            self.grade, self.grade_point = 'C', 5
        else:
            self.grade, self.grade_point = 'RA', 0 # Re-Appear / Fail

        if self.total_marks >= pass_mark and self.grade != 'RA':
            self.result = 'PASS'
        else:
            self.result = 'FAIL'

    def __repr__(self):
        return f'<Mark Student:{self.student_id} Subject:{self.subject_id} Total:{self.total_marks}>'


class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(10), nullable=False, default='Present') # Present, Absent, Late, Excused
    recorded_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    remarks = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    recorded_by = db.relationship('User', foreign_keys=[recorded_by_id])

    __table_args__ = (
        db.UniqueConstraint('student_id', 'subject_id', 'date', name='uq_student_subject_date'),
    )

    def __repr__(self):
        return f'<Attendance Student:{self.student_id} Date:{self.date} Status:{self.status}>'


class Announcement(db.Model):
    __tablename__ = 'announcements'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    target_audience = db.Column(db.String(50), default='All') # All, Students, Faculty, Department
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    priority = db.Column(db.String(20), default='Normal') # Normal, Important, Urgent
    published_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    department_rel = db.relationship('Department', foreign_keys=[department_id])
    published_by = db.relationship('User', foreign_keys=[published_by_id])

    def __repr__(self):
        return f'<Announcement {self.title}>'


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<AuditLog {self.action} by User:{self.user_id}>'


class SystemSetting(db.Model):
    __tablename__ = 'system_settings'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)
    description = db.Column(db.String(255), nullable=True)

    @classmethod
    def get(cls, key, default=None):
        setting = cls.query.filter_by(key=key).first()
        return setting.value if setting and setting.value is not None else default

    @classmethod
    def set(cls, key, value, description=None):
        setting = cls.query.filter_by(key=key).first()
        if not setting:
            setting = cls(key=key, value=str(value), description=description)
            db.session.add(setting)
        else:
            setting.value = str(value)
            if description:
                setting.description = description
        db.session.commit()
        return setting
