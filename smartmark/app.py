import os
import io
import csv
from datetime import datetime, date
from flask import (
    Flask, render_template, redirect, url_for, request,
    jsonify, send_file, flash, abort, Response
)
from flask_login import (
    LoginManager, login_user, logout_user, login_required, current_user
)
from config import Config
from models import (
    db, User, Department, Course, AcademicYear, Semester,
    Student, Faculty, Subject, FacultySubjectAssignment,
    ParentStudent, ExamType, Examination, Mark,
    AttendanceRecord, Announcement, AuditLog, SystemSetting
)
from utils.decorators import (
    role_required, admin_required, super_admin_required,
    faculty_required, student_required, parent_required
)
from utils.grading import (
    calculate_grade_and_points, calculate_sgpa, calculate_cgpa,
    calculate_performance_summary
)
from utils.pdf import generate_marksheet_pdf
from utils.audit import log_action
from utils.seeder import seed_database

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Inject global variables into all templates
@app.context_processor
def inject_global_settings():
    try:
        college_name = SystemSetting.get('college_name', 'SmartMark College of Technology')
        active_ay = SystemSetting.get('active_academic_year', '2025-2026')
    except Exception:
        college_name = 'SmartMark College of Technology'
        active_ay = '2025-2026'
    return dict(app_college_name=college_name, app_active_academic_year=active_ay)

# ==========================================================================
# Authentication & Root Redirection
# ==========================================================================

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role in ['super_admin', 'admin']:
            return redirect(url_for('admin_dashboard'))
        elif current_user.role == 'faculty':
            return redirect(url_for('faculty_dashboard'))
        elif current_user.role == 'student':
            return redirect(url_for('student_dashboard'))
        elif current_user.role == 'parent':
            return redirect(url_for('parent_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # Support sign-in by username OR student register_no
        user = User.query.filter_by(username=username).first()
        if not user:
            student = Student.query.filter_by(register_no=username).first()
            if student:
                user = student.user

        if user and user.check_password(password):
            if not user.is_active_account:
                error = "Account is suspended or deactivated. Please contact the administrator."
            else:
                user.last_login = datetime.utcnow()
                db.session.commit()
                login_user(user)
                log_action(user.id, "LOGIN", f"User {user.username} successfully signed in.")
                flash(f"Welcome back, {user.full_name or user.username}!", "success")
                return redirect(url_for('index'))
        else:
            error = "Invalid username or password. Please verify your credentials."

    return render_template('login.html', error=error)

@app.route('/logout')
@login_required
def logout():
    log_action(current_user.id, "LOGOUT", "User logged out.")
    logout_user()
    flash("You have been signed out safely.", "info")
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def user_profile():
    return render_template('profile.html')

@app.route('/change-password', methods=['POST'])
@login_required
def change_password():
    current_pw = request.form.get('current_password')
    new_pw = request.form.get('new_password')
    confirm_pw = request.form.get('confirm_password')

    if not current_user.check_password(current_pw):
        flash("Current password entered is incorrect.", "danger")
        return redirect(url_for('user_profile'))

    if not new_pw or len(new_pw) < 6:
        flash("New password must contain at least 6 characters.", "danger")
        return redirect(url_for('user_profile'))

    if new_pw != confirm_pw:
        flash("New password and confirmation do not match.", "danger")
        return redirect(url_for('user_profile'))

    current_user.set_password(new_pw)
    db.session.commit()
    log_action(current_user.id, "PASSWORD_CHANGE", "User updated account password.")
    flash("Password updated successfully.", "success")
    return redirect(url_for('user_profile'))

# ==========================================================================
# Administrator Portal Routes
# ==========================================================================

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    total_students = Student.query.count()
    total_faculty = Faculty.query.count()
    total_departments = Department.query.count()
    total_courses = Course.query.count()

    # Pass rate from published marks
    published_marks = Mark.query.filter_by(status='approved').all()
    overall_pass_rate = 0.0
    if published_marks:
        passed = sum(1 for m in published_marks if m.result == 'PASS')
        overall_pass_rate = round((passed / len(published_marks)) * 100, 1)

    # Department Enrollment Distribution for Chart
    departments = Department.query.all()
    dept_labels = [d.name for d in departments]
    dept_counts = [d.students.count() for d in departments]

    # Grade distribution for chart
    grade_order = ['O', 'A+', 'A', 'B+', 'B', 'C', 'RA']
    grade_labels = grade_order
    grade_counts = [sum(1 for m in published_marks if m.grade == g) for g in grade_order]

    # Recent student registrations & audit logs
    recent_students = Student.query.order_by(Student.created_at.desc()).limit(5).all()
    recent_logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(8).all()
    pending_marks_count = Mark.query.filter_by(status='submitted').count()

    return render_template(
        'admin/dashboard.html',
        total_students=total_students,
        total_faculty=total_faculty,
        total_departments=total_departments,
        total_courses=total_courses,
        overall_pass_rate=overall_pass_rate,
        dept_labels=dept_labels,
        dept_counts=dept_counts,
        grade_labels=grade_labels,
        grade_counts=grade_counts,
        recent_students=recent_students,
        recent_logs=recent_logs,
        pending_marks_count=pending_marks_count
    )

@app.route('/admin/students')
@login_required
@admin_required
def admin_students():
    q = request.args.get('q', '').strip()
    dept_id = request.args.get('dept_id', type=int)
    semester = request.args.get('semester', type=int)
    status = request.args.get('status', '').strip()

    query = Student.query
    if q:
        query = query.filter(
            (Student.name.ilike(f"%{q}%")) |
            (Student.register_no.ilike(f"%{q}%")) |
            (Student.email.ilike(f"%{q}%"))
        )
    if dept_id:
        query = query.filter_by(department_id=dept_id)
    if semester:
        query = query.filter_by(current_semester=semester)
    if status:
        query = query.filter_by(enrollment_status=status)

    students = query.order_by(Student.register_no.asc()).all()
    departments = Department.query.filter_by(is_active=True).all()
    courses = Course.query.filter_by(is_active=True).all()

    return render_template(
        'admin/students.html',
        students=students,
        departments=departments,
        courses=courses
    )

@app.route('/admin/students/<int:student_id>')
@login_required
@admin_required
def admin_student_detail(student_id):
    student = Student.query.get_or_404(student_id)
    marks = student.marks.all()
    sgpa = calculate_sgpa(marks)
    cgpa = calculate_cgpa(student)

    # Attendance calculation
    att_records = student.attendance_records.all()
    att_rate = 0.0
    if att_records:
        present_count = sum(1 for a in att_records if a.status in ['Present', 'Late'])
        att_rate = round((present_count / len(att_records)) * 100, 1)

    return render_template(
        'admin/student_detail.html',
        student=student,
        marks=marks,
        sgpa=sgpa,
        cgpa=cgpa,
        attendance_rate=att_rate
    )

@app.route('/admin/students/add', methods=['POST'])
@login_required
@admin_required
def admin_add_student():
    name = request.form.get('name', '').strip()
    register_no = request.form.get('register_no', '').strip().upper()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    dept_id = request.form.get('department_id', type=int)
    course_id = request.form.get('course_id', type=int)
    current_semester = request.form.get('current_semester', type=int, default=1)
    dob_str = request.form.get('date_of_birth')
    gender = request.form.get('gender', 'Male')
    address = request.form.get('address', '').strip()

    if Student.query.filter_by(register_no=register_no).first():
        flash(f"Registration number {register_no} already exists.", "danger")
        return redirect(url_for('admin_students'))

    dob = None
    if dob_str:
        try:
            dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        except Exception:
            pass

    # Create associated user account
    user = User(
        username=register_no.lower(),
        email=email or f"{register_no.lower()}@student.smartmark.edu",
        role='student',
        full_name=name,
        is_active_account=True
    )
    user.set_password('student123')
    db.session.add(user)
    db.session.flush()

    student = Student(
        user_id=user.id,
        register_no=register_no,
        name=name,
        email=email,
        phone=phone,
        address=address,
        department_id=dept_id,
        course_id=course_id,
        admission_year=date.today().year,
        current_semester=current_semester,
        date_of_birth=dob,
        gender=gender,
        enrollment_status='Active'
    )
    db.session.add(student)
    db.session.commit()

    log_action(current_user.id, "STUDENT_CREATE", f"Enrolled student {name} ({register_no}).")
    flash(f"Student {name} registered successfully. Default login password: student123", "success")
    return redirect(url_for('admin_students'))

@app.route('/admin/students/<int:student_id>/edit', methods=['POST'])
@login_required
@admin_required
def admin_edit_student(student_id):
    student = Student.query.get_or_404(student_id)
    student.name = request.form.get('name', '').strip()
    new_reg = request.form.get('register_no', '').strip().upper()
    
    # Check uniqueness if register_no was modified
    if new_reg != student.register_no and Student.query.filter_by(register_no=new_reg).first():
        flash(f"Registration number {new_reg} is already assigned to another student.", "danger")
        return redirect(url_for('admin_students'))

    student.register_no = new_reg
    student.email = request.form.get('email', '').strip()
    student.phone = request.form.get('phone', '').strip()
    student.department_id = request.form.get('department_id', type=int)
    student.course_id = request.form.get('course_id', type=int)
    student.current_semester = request.form.get('current_semester', type=int)
    student.enrollment_status = request.form.get('enrollment_status', 'Active')

    dob_str = request.form.get('date_of_birth')
    if dob_str:
        try:
            student.date_of_birth = datetime.strptime(dob_str, '%Y-%m-%d').date()
        except Exception:
            pass

    # Update associated user
    if student.user:
        student.user.full_name = student.name
        student.user.email = student.email

    db.session.commit()
    log_action(current_user.id, "STUDENT_UPDATE", f"Updated student profile {student.register_no}.")
    flash("Student details updated successfully.", "success")
    return redirect(url_for('admin_students'))

@app.route('/admin/students/<int:student_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def admin_toggle_student_status(student_id):
    student = Student.query.get_or_404(student_id)
    if student.enrollment_status == 'Active':
        student.enrollment_status = 'Inactive'
        if student.user:
            student.user.is_active_account = False
        msg = f"Archived / Deactivated student {student.register_no}."
    else:
        student.enrollment_status = 'Active'
        if student.user:
            student.user.is_active_account = True
        msg = f"Re-activated student {student.register_no}."

    db.session.commit()
    log_action(current_user.id, "STUDENT_STATUS_TOGGLE", msg)
    flash(msg, "info")
    return redirect(url_for('admin_students'))

@app.route('/admin/students/<int:student_id>/reset-password', methods=['POST'])
@login_required
@admin_required
def admin_reset_student_password(student_id):
    student = Student.query.get_or_404(student_id)
    new_pw = request.form.get('new_password', 'student123').strip()
    if student.user:
        student.user.set_password(new_pw)
        db.session.commit()
        log_action(current_user.id, "PASSWORD_RESET", f"Reset password for student {student.register_no}.")
        flash(f"Password reset for {student.name}. New password: {new_pw}", "success")
    return redirect(url_for('admin_student_detail', student_id=student.id))

@app.route('/admin/students/export')
@login_required
@admin_required
def admin_export_students():
    students = Student.query.order_by(Student.register_no.asc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Register No', 'Name', 'Department', 'Programme',
        'Current Semester', 'Age', 'Email', 'Phone', 'Enrollment Status'
    ])
    for s in students:
        writer.writerow([
            s.register_no, s.name, s.department, s.programme,
            s.current_semester, s.age or '', s.email or '', s.phone or '', s.enrollment_status
        ])
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=SmartMark_Students_Directory.csv"}
    )

@app.route('/admin/students/import', methods=['POST'])
@login_required
@admin_required
def admin_import_students():
    file = request.files.get('csv_file')
    if not file or not file.filename.endswith('.csv'):
        flash("Please upload a valid CSV file.", "danger")
        return redirect(url_for('admin_students'))

    try:
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        reader = csv.DictReader(stream)
        imported_count = 0

        default_dept = Department.query.first()
        default_course = Course.query.first()

        for row in reader:
            reg = row.get('register_no', '').strip().upper()
            name = row.get('name', '').strip()
            if not reg or not name:
                continue

            if Student.query.filter_by(register_no=reg).first():
                continue

            u = User(
                username=reg.lower(),
                email=row.get('email', f"{reg.lower()}@student.smartmark.edu"),
                role='student',
                full_name=name
            )
            u.set_password('student123')
            db.session.add(u)
            db.session.flush()

            st = Student(
                user_id=u.id,
                register_no=reg,
                name=name,
                email=row.get('email', ''),
                phone=row.get('phone', ''),
                department_id=default_dept.id if default_dept else None,
                course_id=default_course.id if default_course else None,
                current_semester=int(row.get('semester', 1)),
                gender=row.get('gender', 'Male'),
                enrollment_status='Active'
            )
            db.session.add(st)
            imported_count += 1

        db.session.commit()
        log_action(current_user.id, "STUDENT_IMPORT_CSV", f"Imported {imported_count} students from CSV.")
        flash(f"Successfully imported {imported_count} students.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Failed to parse CSV file: {str(e)}", "danger")

    return redirect(url_for('admin_students'))

# ==========================================================================
# Faculty Management Routes
# ==========================================================================

@app.route('/admin/faculty')
@login_required
@admin_required
def admin_faculty():
    faculty_list = Faculty.query.order_by(Faculty.name.asc()).all()
    departments = Department.query.filter_by(is_active=True).all()
    all_subjects = Subject.query.filter_by(is_active=True).all()
    return render_template(
        'admin/faculty.html',
        faculty_list=faculty_list,
        departments=departments,
        all_subjects=all_subjects
    )

@app.route('/admin/faculty/add', methods=['POST'])
@login_required
@admin_required
def admin_add_faculty():
    name = request.form.get('name', '').strip()
    employee_id = request.form.get('employee_id', '').strip().upper()
    username = request.form.get('username', '').strip().lower()
    dept_id = request.form.get('department_id', type=int)
    designation = request.form.get('designation', 'Assistant Professor')
    qualification = request.form.get('qualification', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()

    if User.query.filter_by(username=username).first():
        flash(f"Username {username} already exists.", "danger")
        return redirect(url_for('admin_faculty'))

    if Faculty.query.filter_by(employee_id=employee_id).first():
        flash(f"Employee ID {employee_id} already exists.", "danger")
        return redirect(url_for('admin_faculty'))

    user = User(
        username=username,
        email=email or f"{username}@smartmark.edu",
        role='faculty',
        full_name=name,
        is_active_account=True
    )
    user.set_password('faculty123')
    db.session.add(user)
    db.session.flush()

    faculty = Faculty(
        user_id=user.id,
        employee_id=employee_id,
        name=name,
        email=email,
        phone=phone,
        department_id=dept_id,
        designation=designation,
        qualification=qualification,
        joining_date=date.today(),
        is_active=True
    )
    db.session.add(faculty)
    db.session.commit()

    log_action(current_user.id, "FACULTY_CREATE", f"Created faculty account for {name} ({employee_id}).")
    flash(f"Faculty member {name} added. Login credentials: {username} / faculty123", "success")
    return redirect(url_for('admin_faculty'))

@app.route('/admin/faculty/<int:faculty_id>/edit', methods=['POST'])
@login_required
@admin_required
def admin_edit_faculty(faculty_id):
    faculty = Faculty.query.get_or_404(faculty_id)
    faculty.name = request.form.get('name', '').strip()
    faculty.employee_id = request.form.get('employee_id', '').strip().upper()
    faculty.department_id = request.form.get('department_id', type=int)
    faculty.designation = request.form.get('designation', '').strip()
    faculty.email = request.form.get('email', '').strip()
    faculty.phone = request.form.get('phone', '').strip()

    if faculty.user:
        faculty.user.full_name = faculty.name
        faculty.user.email = faculty.email

    db.session.commit()
    log_action(current_user.id, "FACULTY_UPDATE", f"Updated faculty member {faculty.employee_id}.")
    flash("Faculty profile updated successfully.", "success")
    return redirect(url_for('admin_faculty'))

@app.route('/admin/faculty/<int:faculty_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def admin_toggle_faculty_status(faculty_id):
    faculty = Faculty.query.get_or_404(faculty_id)
    faculty.is_active = not faculty.is_active
    if faculty.user:
        faculty.user.is_active_account = faculty.is_active

    db.session.commit()
    status_str = "Activated" if faculty.is_active else "Deactivated"
    log_action(current_user.id, "FACULTY_STATUS_TOGGLE", f"{status_str} faculty {faculty.employee_id}.")
    flash(f"Faculty member {status_str}.", "info")
    return redirect(url_for('admin_faculty'))

@app.route('/admin/faculty/assign-subject', methods=['POST'])
@login_required
@admin_required
def admin_assign_subject():
    faculty_id = request.form.get('faculty_id', type=int)
    subject_id = request.form.get('subject_id', type=int)
    section = request.form.get('section', 'A').strip().upper()

    existing = FacultySubjectAssignment.query.filter_by(
        faculty_id=faculty_id, subject_id=subject_id, section=section
    ).first()
    if existing:
        flash("This subject and section is already allocated to this faculty member.", "warning")
        return redirect(url_for('admin_faculty'))

    curr_ay = AcademicYear.query.filter_by(is_current=True).first()
    assignment = FacultySubjectAssignment(
        faculty_id=faculty_id,
        subject_id=subject_id,
        academic_year_id=curr_ay.id if curr_ay else None,
        section=section
    )
    db.session.add(assignment)
    db.session.commit()

    log_action(current_user.id, "FACULTY_ASSIGN_SUBJECT", f"Assigned subject {subject_id} to faculty {faculty_id}.")
    flash("Subject allocated successfully.", "success")
    return redirect(url_for('admin_faculty'))

# ==========================================================================
# Academic Structure: Departments, Courses, Subjects, Semesters
# ==========================================================================

@app.route('/admin/departments-courses')
@login_required
@admin_required
def admin_departments_courses():
    departments = Department.query.all()
    courses = Course.query.all()
    subjects = Subject.query.order_by(Subject.semester.asc(), Subject.subject_code.asc()).all()
    academic_years = AcademicYear.query.order_by(AcademicYear.id.desc()).all()
    semesters = Semester.query.order_by(Semester.semester_number.asc()).all()

    return render_template(
        'admin/departments_courses.html',
        departments=departments,
        courses=courses,
        subjects=subjects,
        academic_years=academic_years,
        semesters=semesters
    )

@app.route('/admin/department/add', methods=['POST'])
@login_required
@admin_required
def admin_add_department():
    code = request.form.get('code', '').strip().upper()
    name = request.form.get('name', '').strip()
    hod = request.form.get('hod_name', '').strip()
    desc = request.form.get('description', '').strip()

    if Department.query.filter_by(code=code).first():
        flash(f"Department code {code} already exists.", "danger")
        return redirect(url_for('admin_departments_courses'))

    dept = Department(code=code, name=name, hod_name=hod, description=desc, is_active=True)
    db.session.add(dept)
    db.session.commit()

    log_action(current_user.id, "DEPARTMENT_CREATE", f"Created department {code} - {name}.")
    flash(f"Department {name} created successfully.", "success")
    return redirect(url_for('admin_departments_courses'))

@app.route('/admin/course/add', methods=['POST'])
@login_required
@admin_required
def admin_add_course():
    code = request.form.get('course_code', '').strip().upper()
    name = request.form.get('name', '').strip()
    dept_id = request.form.get('department_id', type=int)
    degree_type = request.form.get('degree_type', 'Undergraduate')
    duration = request.form.get('duration_years', type=int, default=4)

    if Course.query.filter_by(course_code=code).first():
        flash(f"Course code {code} already exists.", "danger")
        return redirect(url_for('admin_departments_courses'))

    course = Course(
        course_code=code,
        name=name,
        department_id=dept_id,
        degree_type=degree_type,
        duration_years=duration,
        total_semesters=duration * 2,
        is_active=True
    )
    db.session.add(course)
    db.session.commit()

    log_action(current_user.id, "COURSE_CREATE", f"Created course {code} - {name}.")
    flash(f"Degree programme {name} created successfully.", "success")
    return redirect(url_for('admin_departments_courses'))

@app.route('/admin/subject/add', methods=['POST'])
@login_required
@admin_required
def admin_add_subject():
    code = request.form.get('subject_code', '').strip().upper()
    name = request.form.get('subject_name', '').strip()
    dept_id = request.form.get('department_id', type=int)
    course_id = request.form.get('course_id', type=int)
    semester = request.form.get('semester', type=int, default=1)
    credits = request.form.get('credits', type=int, default=3)
    subject_type = request.form.get('subject_type', 'Theory')
    max_internal = request.form.get('max_internal', type=float, default=40.0)
    max_external = request.form.get('max_external', type=float, default=60.0)
    pass_marks = request.form.get('pass_marks', type=float, default=40.0)

    if Subject.query.filter_by(subject_code=code).first():
        flash(f"Subject code {code} already exists.", "danger")
        return redirect(url_for('admin_departments_courses'))

    subject = Subject(
        subject_code=code,
        subject_name=name,
        department_id=dept_id,
        course_id=course_id,
        semester=semester,
        credits=credits,
        subject_type=subject_type,
        max_internal=max_internal,
        max_external=max_external,
        max_marks=max_internal + max_external,
        pass_marks=pass_marks,
        is_active=True
    )
    db.session.add(subject)
    db.session.commit()

    log_action(current_user.id, "SUBJECT_CREATE", f"Added subject {code} - {name}.")
    flash(f"Curriculum subject {name} registered.", "success")
    return redirect(url_for('admin_departments_courses'))

# ==========================================================================
# Examination & Marks Verification Routes
# ==========================================================================

@app.route('/admin/examinations')
@login_required
@admin_required
def admin_examinations():
    examinations = Examination.query.order_by(Examination.id.desc()).all()
    exam_types = ExamType.query.filter_by(is_active=True).all()
    academic_years = AcademicYear.query.all()
    return render_template(
        'admin/examinations.html',
        examinations=examinations,
        exam_types=exam_types,
        academic_years=academic_years
    )

@app.route('/admin/examination/add', methods=['POST'])
@login_required
@admin_required
def admin_add_examination():
    name = request.form.get('name', '').strip()
    exam_type_id = request.form.get('exam_type_id', type=int)
    semester = request.form.get('semester', type=int, default=1)
    ay_id = request.form.get('academic_year_id', type=int)
    start_str = request.form.get('start_date')
    end_str = request.form.get('end_date')

    s_date, e_date = None, None
    if start_str:
        try: s_date = datetime.strptime(start_str, '%Y-%m-%d').date()
        except Exception: pass
    if end_str:
        try: e_date = datetime.strptime(end_str, '%Y-%m-%d').date()
        except Exception: pass

    exam = Examination(
        name=name,
        exam_type_id=exam_type_id,
        semester=semester,
        academic_year_id=ay_id,
        start_date=s_date,
        end_date=e_date,
        status='Scheduled',
        is_published=False
    )
    db.session.add(exam)
    db.session.commit()

    log_action(current_user.id, "EXAM_SCHEDULE", f"Scheduled examination {name}.")
    flash(f"Examination schedule '{name}' created.", "success")
    return redirect(url_for('admin_examinations'))

@app.route('/admin/examination/<int:exam_id>/toggle-publish', methods=['POST'])
@login_required
@admin_required
def admin_toggle_publish_exam(exam_id):
    exam = Examination.query.get_or_404(exam_id)
    exam.is_published = not exam.is_published
    if exam.is_published:
        exam.published_at = datetime.utcnow()
        exam.status = 'Published'
        # Automatically mark all submitted marks under this exam as approved
        Mark.query.filter_by(examination_id=exam.id, status='submitted').update(
            {'status': 'approved', 'approved_by_id': current_user.id}
        )
        msg = f"Published official examination results for {exam.name}. Students can now view marksheets."
    else:
        exam.status = 'In Progress'
        msg = f"Unpublished examination results for {exam.name}. Results locked from student access."

    db.session.commit()
    log_action(current_user.id, "EXAM_PUBLISH_TOGGLE", msg)
    flash(msg, "info")
    return redirect(url_for('admin_examinations'))

@app.route('/admin/marks-approval')
@login_required
@admin_required
def admin_marks_approval():
    pending_marks = Mark.query.filter_by(status='submitted').order_by(Mark.updated_at.desc()).all()
    approved_marks = Mark.query.filter_by(status='approved').order_by(Mark.updated_at.desc()).limit(15).all()
    return render_template(
        'admin/marks_approval.html',
        pending_marks=pending_marks,
        approved_marks=approved_marks
    )

@app.route('/admin/marks/approve/<int:mark_id>', methods=['POST'])
@login_required
@admin_required
def admin_approve_mark(mark_id):
    mark = Mark.query.get_or_404(mark_id)
    mark.status = 'approved'
    mark.approved_by_id = current_user.id
    db.session.commit()
    log_action(current_user.id, "MARK_APPROVE", f"Approved mark for Student {mark.student_id} in Subject {mark.subject_id}.")
    flash("Mark submission verified and officially published.", "success")
    return redirect(url_for('admin_marks_approval'))

@app.route('/admin/marks/reject/<int:mark_id>', methods=['POST'])
@login_required
@admin_required
def admin_reject_mark(mark_id):
    mark = Mark.query.get_or_404(mark_id)
    mark.status = 'draft'
    db.session.commit()
    log_action(current_user.id, "MARK_REJECT", f"Rejected mark for Student {mark.student_id} back to draft.")
    flash("Mark submission returned to faculty draft.", "warning")
    return redirect(url_for('admin_marks_approval'))

@app.route('/admin/marks/batch-approve', methods=['POST'])
@login_required
@admin_required
def admin_batch_approve_marks():
    updated = Mark.query.filter_by(status='submitted').update({
        'status': 'approved',
        'approved_by_id': current_user.id
    })
    db.session.commit()
    log_action(current_user.id, "MARKS_BATCH_APPROVE", f"Bulk-approved {updated} marks records.")
    flash(f"Approved {updated} pending mark submissions successfully.", "success")
    return redirect(url_for('admin_marks_approval'))

# ==========================================================================
# Attendance, Announcements, Reports & Audit
# ==========================================================================

@app.route('/admin/attendance')
@login_required
@admin_required
def admin_attendance():
    all_students = Student.query.filter_by(enrollment_status='Active').all()
    student_records = []
    low_attendance_students = []

    total_conducted = 0
    total_attended = 0

    for st in all_students:
        records = st.attendance_records.all()
        cnt = len(records)
        att = sum(1 for r in records if r.status in ['Present', 'Late'])
        pct = round((att / cnt) * 100, 1) if cnt > 0 else 100.0

        item = {
            'student': st,
            'total': cnt,
            'attended': att,
            'percent': pct
        }
        student_records.append(item)
        if cnt > 0 and pct < 75.0:
            low_attendance_students.append(item)

        total_conducted += cnt
        total_attended += att

    overall_att = round((total_attended / total_conducted) * 100, 1) if total_conducted > 0 else 92.5

    return render_template(
        'admin/attendance.html',
        overall_attendance=overall_att,
        low_attendance_students=low_attendance_students,
        all_attendance_records=student_records
    )

@app.route('/admin/attendance/export')
@login_required
@admin_required
def admin_export_attendance():
    students = Student.query.filter_by(enrollment_status='Active').all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Register No', 'Student Name', 'Department', 'Semester', 'Attended', 'Total Classes', 'Percentage (%)', 'Eligibility'])

    for st in students:
        records = st.attendance_records.all()
        cnt = len(records)
        att = sum(1 for r in records if r.status in ['Present', 'Late'])
        pct = round((att / cnt) * 100, 1) if cnt > 0 else 100.0
        elig = 'Eligible' if pct >= 75.0 else 'Shortage Warning'
        writer.writerow([st.register_no, st.name, st.department, st.current_semester, att, cnt, pct, elig])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=SmartMark_Attendance_Roster.csv"}
    )

@app.route('/admin/announcements')
@login_required
@admin_required
def admin_announcements():
    announcements = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template('admin/announcements.html', announcements=announcements)

@app.route('/admin/announcement/add', methods=['POST'])
@login_required
@admin_required
def admin_add_announcement():
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    target = request.form.get('target_audience', 'All')
    priority = request.form.get('priority', 'Normal')

    ann = Announcement(
        title=title,
        content=content,
        target_audience=target,
        priority=priority,
        published_by_id=current_user.id,
        is_active=True
    )
    db.session.add(ann)
    db.session.commit()

    log_action(current_user.id, "ANNOUNCEMENT_CREATE", f"Published announcement: {title}")
    flash("Campus announcement broadcasted successfully.", "success")
    return redirect(url_for('admin_announcements'))

@app.route('/admin/announcement/<int:announcement_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_announcement(announcement_id):
    ann = Announcement.query.get_or_404(announcement_id)
    db.session.delete(ann)
    db.session.commit()
    flash("Announcement deleted.", "info")
    return redirect(url_for('admin_announcements'))

@app.route('/admin/reports')
@login_required
@admin_required
def admin_reports():
    # 1. Top students
    active_students = Student.query.filter_by(enrollment_status='Active').all()
    ranked_students = []
    for st in active_students:
        marks = st.marks.filter_by(status='approved').all()
        if marks:
            sgpa = calculate_sgpa(marks)
            cgpa = calculate_cgpa(st)
            ranked_students.append((st, sgpa, cgpa))
    
    ranked_students.sort(key=lambda x: (x[2], x[1]), reverse=True)
    top_students = [(idx + 1, item[0], item[1], item[2]) for idx, item in enumerate(ranked_students[:8])]

    # 2. Students needing support (Failed / RA marks)
    failed_marks = Mark.query.filter_by(result='FAIL').all()

    # 3. Department summaries
    dept_summaries = []
    for d in Department.query.all():
        marks_d = Mark.query.join(Student).filter(Student.department_id == d.id, Mark.status == 'approved').all()
        pass_count = sum(1 for m in marks_d if m.result == 'PASS')
        pass_rate = round((pass_count / len(marks_d)) * 100, 1) if marks_d else 85.0
        dept_summaries.append({
            'code': d.code,
            'name': d.name,
            'courses_count': d.courses.count(),
            'students_count': d.students.count(),
            'faculty_count': d.faculty_members.count(),
            'pass_rate': pass_rate
        })

    return render_template(
        'admin/reports.html',
        top_students=top_students,
        failed_marks=failed_marks,
        dept_summaries=dept_summaries
    )

@app.route('/admin/reports/export/<report_type>')
@login_required
@admin_required
def admin_export_reports(report_type):
    output = io.StringIO()
    writer = csv.writer(output)

    if report_type == 'toppers':
        writer.writerow(['Rank', 'Register No', 'Student Name', 'Department', 'Semester', 'SGPA', 'CGPA'])
        active_students = Student.query.filter_by(enrollment_status='Active').all()
        ranked = []
        for st in active_students:
            m = st.marks.filter_by(status='approved').all()
            if m: ranked.append((st, calculate_sgpa(m), calculate_cgpa(st)))
        ranked.sort(key=lambda x: (x[2], x[1]), reverse=True)
        for idx, (st, sgpa, cgpa) in enumerate(ranked, start=1):
            writer.writerow([idx, st.register_no, st.name, st.department, st.current_semester, sgpa, cgpa])

    elif report_type == 'support':
        writer.writerow(['Register No', 'Student Name', 'Department', 'Subject Code', 'Subject Name', 'Marks Obtained', 'Pass Threshold'])
        for m in Mark.query.filter_by(result='FAIL').all():
            writer.writerow([m.student.register_no, m.student.name, m.student.department, m.subject.subject_code, m.subject.subject_name, m.total_marks, m.subject.pass_marks])

    else: # departments
        writer.writerow(['Department Code', 'Department Name', 'Degree Courses', 'Enrolled Students', 'Faculty Count'])
        for d in Department.query.all():
            writer.writerow([d.code, d.name, d.courses.count(), d.students.count(), d.faculty_members.count()])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=SmartMark_{report_type}_Report.csv"}
    )

@app.route('/admin/audit-logs')
@login_required
@admin_required
def admin_audit_logs():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(100).all()
    return render_template('admin/audit_logs.html', logs=logs)

@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
@super_admin_required
def admin_settings():
    if request.method == 'POST':
        for k in ['college_name', 'college_code', 'contact_email', 'college_address', 'min_attendance_percent', 'pass_mark_cutoff']:
            val = request.form.get(k)
            if val is not None:
                SystemSetting.set(k, val)
        
        att_enabled = 'true' if request.form.get('attendance_module_enabled') else 'false'
        SystemSetting.set('attendance_module_enabled', att_enabled)

        log_action(current_user.id, "SETTINGS_UPDATE", "Updated institutional system settings.")
        flash("System governance settings saved successfully.", "success")

    settings_dict = {s.key: s.value for s in SystemSetting.query.all()}
    return render_template('admin/settings.html', settings=settings_dict)

# ==========================================================================
# Faculty Portal Routes
# ==========================================================================

@app.route('/faculty/dashboard')
@login_required
@faculty_required
def faculty_dashboard():
    faculty = current_user.faculty
    if not faculty:
        flash("No faculty profile associated with your user account.", "danger")
        return redirect(url_for('index'))

    assigned_subjects = faculty.assignments.all()
    total_students_taught = 0
    pending_drafts_count = 0

    for a in assigned_subjects:
        # Count students in the subject's semester and department
        st_count = Student.query.filter_by(
            department_id=a.subject.department_id,
            current_semester=a.subject.semester,
            enrollment_status='Active'
        ).count()
        total_students_taught += st_count

        drafts = Mark.query.filter_by(subject_id=a.subject_id, status='draft').count()
        pending_drafts_count += drafts

    upcoming_exams = Examination.query.filter_by(is_published=False).order_by(Examination.id.desc()).limit(5).all()

    return render_template(
        'faculty/dashboard.html',
        faculty=faculty,
        assigned_subjects=assigned_subjects,
        total_students_taught=total_students_taught,
        pending_drafts_count=pending_drafts_count,
        upcoming_exams=upcoming_exams
    )

@app.route('/faculty/marks-entry')
@login_required
@faculty_required
def faculty_marks_entry():
    faculty = current_user.faculty
    assigned_subjects = faculty.assignments.all() if faculty else []
    examinations = Examination.query.order_by(Examination.id.desc()).all()

    subject_id = request.args.get('subject_id', type=int)
    examination_id = request.args.get('examination_id', type=int)

    selected_subject = None
    selected_exam = None
    student_marks_data = []

    if subject_id:
        selected_subject = Subject.query.get(subject_id)
    elif assigned_subjects:
        selected_subject = assigned_subjects[0].subject

    if examination_id:
        selected_exam = Examination.query.get(examination_id)
    elif examinations:
        selected_exam = examinations[0]

    if selected_subject and selected_exam:
        students = Student.query.filter_by(
            department_id=selected_subject.department_id,
            current_semester=selected_subject.semester,
            enrollment_status='Active'
        ).order_by(Student.register_no.asc()).all()

        for st in students:
            m = Mark.query.filter_by(
                student_id=st.id,
                subject_id=selected_subject.id,
                examination_id=selected_exam.id
            ).first()
            student_marks_data.append({'student': st, 'mark': m})

    return render_template(
        'faculty/marks_entry.html',
        assigned_subjects=assigned_subjects,
        examinations=examinations,
        selected_subject=selected_subject,
        selected_exam=selected_exam,
        student_marks_data=student_marks_data
    )

@app.route('/faculty/marks/save', methods=['POST'])
@login_required
@faculty_required
def faculty_save_marks():
    subject_id = request.form.get('subject_id', type=int)
    examination_id = request.form.get('examination_id', type=int)
    action_type = request.form.get('action', 'draft') # 'draft' or 'submit'

    subject = Subject.query.get_or_404(subject_id)
    student_ids = request.form.getlist('student_ids')

    saved_count = 0
    for sid_str in student_ids:
        try:
            sid = int(sid_str)
            int_val = float(request.form.get(f'internal_{sid}', 0.0))
            ext_val = float(request.form.get(f'external_{sid}', 0.0))

            # Backend Validation: Bounds check
            int_val = max(0.0, min(int_val, subject.max_internal))
            ext_val = max(0.0, min(ext_val, subject.max_external))

            mark = Mark.query.filter_by(
                student_id=sid, subject_id=subject.id, examination_id=examination_id
            ).first()

            if not mark:
                mark = Mark(
                    student_id=sid,
                    subject_id=subject.id,
                    examination_id=examination_id,
                    entered_by_id=current_user.id
                )
                db.session.add(mark)

            # Do not allow modifying locked approved marks unless admin
            if mark.status == 'approved' and current_user.role not in ['admin', 'super_admin']:
                continue

            mark.internal_marks = round(int_val * 0.7, 1)
            mark.assignment_marks = round(int_val * 0.3, 1)
            mark.external_marks = ext_val
            mark.status = 'submitted' if action_type == 'submit' else 'draft'
            mark.entered_by_id = current_user.id
            mark.calculate_results(pass_mark=subject.pass_marks)
            saved_count += 1
        except Exception:
            continue

    db.session.commit()
    msg = f"Submitted {saved_count} marks records for administrator approval." if action_type == 'submit' else f"Saved {saved_count} marks records as draft."
    log_action(current_user.id, "MARKS_ENTRY", msg)
    flash(msg, "success")
    return redirect(url_for('faculty_marks_entry', subject_id=subject_id, examination_id=examination_id))

@app.route('/faculty/attendance-entry')
@login_required
@faculty_required
def faculty_attendance_entry():
    faculty = current_user.faculty
    assigned_subjects = faculty.assignments.all() if faculty else []
    subject_id = request.args.get('subject_id', type=int)
    date_str = request.args.get('date', date.today().strftime('%Y-%m-%d'))

    selected_subject = None
    if subject_id:
        selected_subject = Subject.query.get(subject_id)
    elif assigned_subjects:
        selected_subject = assigned_subjects[0].subject

    roster = []
    if selected_subject:
        try: att_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except Exception: att_date = date.today()

        students = Student.query.filter_by(
            department_id=selected_subject.department_id,
            current_semester=selected_subject.semester,
            enrollment_status='Active'
        ).order_by(Student.register_no.asc()).all()

        for st in students:
            rec = AttendanceRecord.query.filter_by(
                student_id=st.id, subject_id=selected_subject.id, date=att_date
            ).first()
            roster.append({'student': st, 'record': rec})

    return render_template(
        'faculty/attendance_entry.html',
        assigned_subjects=assigned_subjects,
        selected_subject=selected_subject,
        selected_date=date_str,
        roster=roster
    )

@app.route('/faculty/attendance/save', methods=['POST'])
@login_required
@faculty_required
def faculty_save_attendance():
    subject_id = request.form.get('subject_id', type=int)
    date_str = request.form.get('date')
    student_ids = request.form.getlist('student_ids')

    try: att_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except Exception: att_date = date.today()

    saved = 0
    for sid_str in student_ids:
        try:
            sid = int(sid_str)
            status = request.form.get(f'status_{sid}', 'Present')
            remarks = request.form.get(f'remarks_{sid}', '').strip()

            rec = AttendanceRecord.query.filter_by(
                student_id=sid, subject_id=subject_id, date=att_date
            ).first()

            if not rec:
                rec = AttendanceRecord(
                    student_id=sid,
                    subject_id=subject_id,
                    date=att_date,
                    recorded_by_id=current_user.id
                )
                db.session.add(rec)

            rec.status = status
            rec.remarks = remarks
            saved += 1
        except Exception:
            continue

    db.session.commit()
    log_action(current_user.id, "ATTENDANCE_RECORD", f"Recorded attendance for {saved} students in subject {subject_id} on {att_date}.")
    flash(f"Recorded attendance for {saved} students.", "success")
    return redirect(url_for('faculty_attendance_entry', subject_id=subject_id, date=date_str))

# ==========================================================================
# Student Portal Routes
# ==========================================================================

@app.route('/student/dashboard')
@login_required
@student_required
def student_dashboard():
    student = current_user.student
    if not student:
        flash("No student profile linked to this account.", "danger")
        return redirect(url_for('login'))

    # Only show approved / published marks to students
    published_marks = student.marks.filter_by(status='approved').all()
    sgpa = calculate_sgpa(published_marks)
    cgpa = calculate_cgpa(student)

    # Attendance
    att_records = student.attendance_records.all()
    att_rate = 0.0
    if att_records:
        present = sum(1 for a in att_records if a.status in ['Present', 'Late'])
        att_rate = round((present / len(att_records)) * 100, 1)

    # Total credits
    total_credits = sum((m.subject.credits or 3) for m in published_marks if m.subject)
    overall_result = 'PASS' if all(m.result == 'PASS' for m in published_marks) and published_marks else ('FAIL' if published_marks else 'PENDING')

    # Chart data
    subject_names = [m.subject.subject_name[:18] for m in published_marks if m.subject]
    subject_scores = [m.total_marks for m in published_marks]

    # Announcements targeting All or Students
    announcements = Announcement.query.filter(
        Announcement.is_active == True,
        Announcement.target_audience.in_(['All', 'Students'])
    ).order_by(Announcement.created_at.desc()).limit(3).all()

    return render_template(
        'student/dashboard.html',
        student=student,
        marks=published_marks,
        sgpa=sgpa,
        cgpa=cgpa,
        attendance_rate=att_rate,
        total_credits=total_credits,
        overall_result=overall_result,
        subject_names=subject_names,
        subject_scores=subject_scores,
        announcements=announcements
    )

@app.route('/student/marksheet')
@login_required
def student_marksheet():
    # Student viewing own marksheet, or Admin/Parent
    student = None
    if current_user.role == 'student':
        student = current_user.student
    elif current_user.role in ['admin', 'super_admin']:
        student_id = request.args.get('student_id', type=int)
        student = Student.query.get_or_404(student_id) if student_id else Student.query.first()
    elif current_user.role == 'parent':
        plink = current_user.parent_links.first()
        student = plink.student if plink else None

    if not student:
        flash("No student record found.", "danger")
        return redirect(url_for('index'))

    published_marks = student.marks.filter_by(status='approved').all()
    sgpa = calculate_sgpa(published_marks)
    cgpa = calculate_cgpa(student)
    total_credits = sum((m.subject.credits or 3) for m in published_marks if m.subject)
    overall_result = 'PASS' if all(m.result == 'PASS' for m in published_marks) and published_marks else ('FAIL' if published_marks else 'PENDING')
    pub_date = datetime.now().strftime('%d-%b-%Y')

    return render_template(
        'student/marksheet.html',
        student=student,
        marks=published_marks,
        sgpa=sgpa,
        cgpa=cgpa,
        total_credits=total_credits,
        overall_result=overall_result,
        pub_date=pub_date
    )

@app.route('/student/attendance')
@login_required
@student_required
def student_attendance():
    student = current_user.student
    all_records = student.attendance_records.all()
    total_conducted = len(all_records)
    total_attended = sum(1 for r in all_records if r.status in ['Present', 'Late'])
    overall_pct = round((total_attended / total_conducted) * 100, 1) if total_conducted > 0 else 100.0

    # Group by subject
    subjects = Subject.query.filter_by(
        department_id=student.department_id, semester=student.current_semester
    ).all()

    subject_att = []
    for s in subjects:
        s_recs = [r for r in all_records if r.subject_id == s.id]
        s_tot = len(s_recs)
        s_att = sum(1 for r in s_recs if r.status in ['Present', 'Late'])
        s_pct = round((s_att / s_tot) * 100, 1) if s_tot > 0 else 100.0
        subject_att.append({
            'subject': s,
            'total': s_tot,
            'attended': s_att,
            'percent': s_pct
        })

    return render_template(
        'student/attendance.html',
        student=student,
        overall_attendance=overall_pct,
        subject_attendance=subject_att
    )

# ==========================================================================
# Parent Portal Routes
# ==========================================================================

@app.route('/parent/dashboard')
@login_required
@parent_required
def parent_dashboard():
    parent_links = current_user.parent_links.all()
    linked_wards = []

    for pl in parent_links:
        st = pl.student
        marks = st.marks.filter_by(status='approved').all()
        sgpa = calculate_sgpa(marks)
        cgpa = calculate_cgpa(st)

        att_records = st.attendance_records.all()
        att_rate = 0.0
        if att_records:
            present = sum(1 for a in att_records if a.status in ['Present', 'Late'])
            att_rate = round((present / len(att_records)) * 100, 1)

        linked_wards.append({
            'student': st,
            'marks': marks,
            'sgpa': sgpa,
            'cgpa': cgpa,
            'attendance_rate': att_rate
        })

    return render_template('parent/dashboard.html', linked_wards=linked_wards)

# ==========================================================================
# Official PDF Marksheet Generation
# ==========================================================================

@app.route('/download/marksheet/<int:student_id>/<int:semester>')
@login_required
def download_marksheet(student_id, semester):
    student = Student.query.get_or_404(student_id)

    # Resource-level access authorization check
    if current_user.role == 'student':
        if not current_user.student or current_user.student.id != student.id:
            abort(403)
    elif current_user.role == 'parent':
        linked_ids = [l.student_id for l in current_user.parent_links]
        if student.id not in linked_ids:
            abort(403)

    # For students/parents, only include approved marks
    if current_user.role in ['student', 'parent']:
        marks = student.marks.filter_by(status='approved').all()
    else:
        marks = student.marks.all()

    sgpa = calculate_sgpa(marks)
    cgpa = calculate_cgpa(student)

    pdf_buffer = generate_marksheet_pdf(student, marks, sgpa, cgpa)
    log_action(current_user.id, "DOWNLOAD_MARKSHEET_PDF", f"Generated marksheet PDF for student {student.register_no}.")

    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        download_name=f"{student.register_no}_Official_Marksheet.pdf",
        as_attachment=True
    )

# ==========================================================================
# CLI Commands & Database Initialization
# ==========================================================================

@app.cli.command('initdb')
def initdb_command():
    db.create_all()
    seed_database()
    print('Database initialized with complete collegiate schema and sample data.')

def init_db():
    """Initialize database tables and seed data if empty."""
    db.create_all()
    # Auto-seed on first run if no users exist
    if User.query.first() is None:
        try:
            seed_database()
            print('Database seeded with initial data.')
        except Exception as e:
            print(f'Seeding skipped or failed: {e}')

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True, port=5000)
