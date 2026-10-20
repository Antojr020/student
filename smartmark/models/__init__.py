from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .core import (
    Department,
    Course,
    AcademicYear,
    Semester,
    Student,
    Faculty,
    Subject,
    FacultySubjectAssignment,
    ParentStudent,
    ExamType,
    Examination,
    Mark,
    AttendanceRecord,
    Announcement,
    AuditLog,
    SystemSetting
)
