from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3

db = SQLAlchemy()

# Enable Write-Ahead Logging (WAL) and synchronous=NORMAL on SQLite connections
# This eliminates "database is locked" errors during concurrent web requests
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.close()
        except Exception:
            pass

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
