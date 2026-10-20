from datetime import date, datetime, timedelta
import random
from models import (
    db, User, Department, Course, AcademicYear, Semester,
    Student, Faculty, Subject, FacultySubjectAssignment,
    ParentStudent, ExamType, Examination, Mark,
    AttendanceRecord, Announcement, AuditLog, SystemSetting
)

def seed_database():
    """
    Populate the database with a complete, realistic collegiate ecosystem:
    departments, courses, faculty, students, exams, marks, attendance, announcements, and settings.
    """
    print("Starting database seeding...")

    # 1. System Settings
    settings = {
        'college_name': 'SmartMark College of Engineering & Technology',
        'college_code': 'SMCET-2026',
        'college_address': 'Technology Park Highway, Chennai, Tamil Nadu 600001',
        'contact_email': 'academics@smartmark.edu',
        'attendance_module_enabled': 'true',
        'min_attendance_percent': '75',
        'pass_mark_cutoff': '40',
        'active_academic_year': '2025-2026'
    }
    for k, v in settings.items():
        SystemSetting.set(k, v)

    # 2. Academic Years & Semesters
    ay_prev = AcademicYear.query.filter_by(year_name='2024-2025').first()
    if not ay_prev:
        ay_prev = AcademicYear(
            year_name='2024-2025',
            is_current=False,
            start_date=date(2024, 7, 1),
            end_date=date(2025, 5, 30)
        )
        db.session.add(ay_prev)

    ay_curr = AcademicYear.query.filter_by(year_name='2025-2026').first()
    if not ay_curr:
        ay_curr = AcademicYear(
            year_name='2025-2026',
            is_current=True,
            start_date=date(2025, 7, 1),
            end_date=date(2026, 5, 30)
        )
        db.session.add(ay_curr)
    db.session.flush()

    # Configure Semesters for current AY
    for sem_num in range(1, 9):
        sem_name = f"Semester {sem_num} ({'Odd' if sem_num % 2 == 1 else 'Even'} AY 25-26)"
        if not Semester.query.filter_by(semester_number=sem_num, academic_year_id=ay_curr.id).first():
            sem = Semester(
                semester_number=sem_num,
                semester_name=sem_name,
                academic_year_id=ay_curr.id,
                is_current=(sem_num == 4) # Set Semester 4 as active semester
            )
            db.session.add(sem)
    db.session.flush()

    # 3. Departments
    dept_specs = [
        ('CSE', 'Computer Science and Engineering', 'Dr. Alan Turing', 'Focuses on algorithms, software architecture, artificial intelligence, and cloud systems.'),
        ('IT', 'Information Technology', 'Dr. Grace Hopper', 'Covers software engineering, database administration, information security, and web technologies.'),
        ('ECE', 'Electronics and Communication Engineering', 'Dr. Claude Shannon', 'Encompasses embedded systems, signal processing, VLSI design, and telecommunications.'),
        ('MECH', 'Mechanical Engineering', 'Dr. James Watt', 'Focuses on thermal engineering, robotics, CAD/CAM design, and industrial manufacturing.'),
        ('CIVIL', 'Civil Engineering', 'Dr. Arthur Casagrande', 'Covers structural analysis, environmental engineering, geotechnical mechanics, and urban planning.')
    ]
    dept_map = {}
    for code, name, hod, desc in dept_specs:
        dept = Department.query.filter_by(code=code).first()
        if not dept:
            dept = Department(code=code, name=name, hod_name=hod, description=desc, is_active=True)
            db.session.add(dept)
            db.session.flush()
        dept_map[code] = dept

    # 4. Courses / Programmes
    course_specs = [
        ('BTECH-CSE', 'B.Tech in Computer Science & Engineering', 'CSE', 'Undergraduate', 4, 8),
        ('BTECH-IT', 'B.Tech in Information Technology', 'IT', 'Undergraduate', 4, 8),
        ('BTECH-ECE', 'B.Tech in Electronics & Communication', 'ECE', 'Undergraduate', 4, 8),
        ('MCA', 'Master of Computer Applications', 'CSE', 'Postgraduate', 2, 4),
        ('MTECH-CSE', 'M.Tech in Advanced Computer Science', 'CSE', 'Postgraduate', 2, 4)
    ]
    course_map = {}
    for code, name, dept_code, deg_type, duration, total_sem in course_specs:
        c = Course.query.filter_by(course_code=code).first()
        if not c:
            c = Course(
                course_code=code,
                name=name,
                department_id=dept_map[dept_code].id,
                degree_type=deg_type,
                duration_years=duration,
                total_semesters=total_sem,
                is_active=True
            )
            db.session.add(c)
            db.session.flush()
        course_map[code] = c

    # 5. Core Users (Super Admin & College Admin)
    # Super Admin
    super_admin_user = User.query.filter_by(username='superadmin').first()
    if not super_admin_user:
        super_admin_user = User(
            username='superadmin',
            email='superadmin@smartmark.edu',
            role='super_admin',
            full_name='Dr. Alexander Wright',
            is_active_account=True
        )
        super_admin_user.set_password('Password@123')
        db.session.add(super_admin_user)

    # College Admin
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@smartmark.edu',
            role='admin',
            full_name='Prof. Sarah Jenkins',
            is_active_account=True
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
    db.session.flush()

    # 6. Faculty Members
    faculty_specs = [
        ('faculty_cs', 'Dr. Alan Turing', 'alan.turing@smartmark.edu', '9876543210', 'CSE', 'Professor & HOD', 'Ph.D in Computer Science, Cambridge', 'EMP-CSE-001'),
        ('faculty_it', 'Dr. Grace Hopper', 'grace.hopper@smartmark.edu', '9876543211', 'IT', 'Associate Professor', 'Ph.D in Applied Mathematics, Yale', 'EMP-IT-001'),
        ('faculty_ece', 'Dr. Claude Shannon', 'claude.shannon@smartmark.edu', '9876543212', 'ECE', 'Assistant Professor', 'Ph.D in Electrical Engineering, MIT', 'EMP-ECE-001'),
        ('faculty_ds', 'Dr. Ada Lovelace', 'ada.lovelace@smartmark.edu', '9876543213', 'CSE', 'Associate Professor', 'M.Tech & Ph.D in Data Science', 'EMP-CSE-002'),
        ('faculty_se', 'Prof. Linus Torvalds', 'linus.torvalds@smartmark.edu', '9876543214', 'IT', 'Assistant Professor', 'M.S. in Computer Engineering, Helsinki', 'EMP-IT-002')
    ]
    faculty_map = {}
    for uname, fname, femail, fphone, fdept, fdesig, fqual, empid in faculty_specs:
        u = User.query.filter_by(username=uname).first()
        if not u:
            u = User(username=uname, email=femail, role='faculty', full_name=fname, is_active_account=True)
            u.set_password('faculty123')
            db.session.add(u)
            db.session.flush()

        fac = Faculty.query.filter_by(user_id=u.id).first()
        if not fac:
            fac = Faculty(
                user_id=u.id,
                employee_id=empid,
                name=fname,
                email=femail,
                phone=fphone,
                department_id=dept_map[fdept].id,
                designation=fdesig,
                qualification=fqual,
                joining_date=date(2021, 6, 1),
                is_active=True
            )
            db.session.add(fac)
            db.session.flush()
        faculty_map[uname] = fac

    # 7. Subjects (Semester 4 - B.Tech CSE & IT)
    subject_specs = [
        ('CS401', 'Database Management Systems', 'CSE', 'BTECH-CSE', 4, 4, 'Theory', 40.0, 60.0, 100.0, 'faculty_cs'),
        ('CS402', 'Operating Systems & Architecture', 'CSE', 'BTECH-CSE', 4, 4, 'Theory', 40.0, 60.0, 100.0, 'faculty_se'),
        ('CS403', 'Design and Analysis of Algorithms', 'CSE', 'BTECH-CSE', 4, 3, 'Theory', 40.0, 60.0, 100.0, 'faculty_cs'),
        ('CS404', 'Machine Learning Foundations', 'CSE', 'BTECH-CSE', 4, 3, 'Theory', 40.0, 60.0, 100.0, 'faculty_ds'),
        ('CS405', 'DBMS & Web Technologies Laboratory', 'CSE', 'BTECH-CSE', 4, 2, 'Practical', 50.0, 50.0, 100.0, 'faculty_cs'),
        ('IT401', 'Web Systems & Cloud Infrastructure', 'IT', 'BTECH-IT', 4, 4, 'Theory', 40.0, 60.0, 100.0, 'faculty_it'),
        ('IT402', 'Network Security and Cryptography', 'IT', 'BTECH-IT', 4, 3, 'Theory', 40.0, 60.0, 100.0, 'faculty_it'),
        ('EC401', 'Signals and Communication Systems', 'ECE', 'BTECH-ECE', 4, 4, 'Theory', 40.0, 60.0, 100.0, 'faculty_ece')
    ]
    subject_map = {}
    for code, sname, dept_code, ccode, ssem, scredits, stype, maxi, maxe, maxt, assigned_fac_key in subject_specs:
        s = Subject.query.filter_by(subject_code=code).first()
        if not s:
            s = Subject(
                subject_code=code,
                subject_name=sname,
                department_id=dept_map[dept_code].id,
                course_id=course_map[ccode].id,
                semester=ssem,
                credits=scredits,
                subject_type=stype,
                max_internal=maxi,
                max_external=maxe,
                max_marks=maxt,
                pass_marks=40.0,
                is_active=True
            )
            db.session.add(s)
            db.session.flush()
        subject_map[code] = s

        # Faculty Assignment
        fac_obj = faculty_map[assigned_fac_key]
        assignment = FacultySubjectAssignment.query.filter_by(faculty_id=fac_obj.id, subject_id=s.id).first()
        if not assignment:
            assignment = FacultySubjectAssignment(
                faculty_id=fac_obj.id,
                subject_id=s.id,
                academic_year_id=ay_curr.id,
                section='A'
            )
            db.session.add(assignment)
    db.session.flush()

    # 8. Exam Types & Examinations
    exam_type_specs = [
        ('Internal Assessment 1', 'IA-1', 20.0, 'First mid-semester theory and assignment review'),
        ('Internal Assessment 2', 'IA-2', 20.0, 'Second mid-semester performance test'),
        ('Model Examination', 'MODEL', 10.0, 'Full syllabus preparatory examination'),
        ('Semester Final Examination', 'SEM-FINAL', 50.0, 'Comprehensive university end-term examination')
    ]
    exam_type_map = {}
    for name, code, weight, desc in exam_type_specs:
        et = ExamType.query.filter_by(code=code).first()
        if not et:
            et = ExamType(name=name, code=code, weightage_percent=weight, description=desc, is_active=True)
            db.session.add(et)
            db.session.flush()
        exam_type_map[code] = et

    # Create active examinations for Semester 4
    exam_sem4 = Examination.query.filter_by(name='Semester 4 Final Examination 2025-26').first()
    if not exam_sem4:
        exam_sem4 = Examination(
            exam_type_id=exam_type_map['SEM-FINAL'].id,
            name='Semester 4 Final Examination 2025-26',
            academic_year_id=ay_curr.id,
            semester=4,
            start_date=date(2025, 11, 10),
            end_date=date(2025, 11, 28),
            status='Published',
            is_published=True,
            published_at=datetime.utcnow() - timedelta(days=5)
        )
        db.session.add(exam_sem4)
        db.session.flush()

    exam_ia1 = Examination.query.filter_by(name='Internal Assessment 1 - Sem 4').first()
    if not exam_ia1:
        exam_ia1 = Examination(
            exam_type_id=exam_type_map['IA-1'].id,
            name='Internal Assessment 1 - Sem 4',
            academic_year_id=ay_curr.id,
            semester=4,
            start_date=date(2025, 8, 15),
            end_date=date(2025, 8, 22),
            status='Published',
            is_published=True,
            published_at=datetime.utcnow() - timedelta(days=45)
        )
        db.session.add(exam_ia1)
        db.session.flush()

    # 9. Students
    student_specs = [
        # (username, name, email, phone, regno, dept_code, course_code, sem, dob, gender, status)
        ('student_arun', 'Arun Kumar', 'arun.kumar@student.smartmark.edu', '9840112233', '2024CSE001', 'CSE', 'BTECH-CSE', 4, date(2004, 5, 14), 'Male', 'Active'),
        ('student_priya', 'Priya Sharma', 'priya.sharma@student.smartmark.edu', '9840112234', '2024CSE002', 'CSE', 'BTECH-CSE', 4, date(2004, 8, 22), 'Female', 'Active'),
        ('student_rahul', 'Rahul Verma', 'rahul.verma@student.smartmark.edu', '9840112235', '2024IT001', 'IT', 'BTECH-IT', 4, date(2003, 11, 30), 'Male', 'Active'),
        ('student_ananya', 'Ananya Iyer', 'ananya.iyer@student.smartmark.edu', '9840112236', '2024ECE001', 'ECE', 'BTECH-ECE', 4, date(2004, 2, 18), 'Female', 'Active'),
        ('student_vikram', 'Vikram Patel', 'vikram.patel@student.smartmark.edu', '9840112237', '2024CSE003', 'CSE', 'BTECH-CSE', 4, date(2004, 7, 9), 'Male', 'Active'),
        ('student_deepa', 'Deepa Nair', 'deepa.nair@student.smartmark.edu', '9840112238', '2024CSE004', 'CSE', 'BTECH-CSE', 4, date(2004, 9, 25), 'Female', 'Active'),
        ('student_karthik', 'Karthik Subramanian', 'karthik.s@student.smartmark.edu', '9840112239', '2024CSE005', 'CSE', 'BTECH-CSE', 4, date(2003, 12, 12), 'Male', 'Active'),
        ('student_sneha', 'Sneha Reddy', 'sneha.reddy@student.smartmark.edu', '9840112240', '2024IT002', 'IT', 'BTECH-IT', 4, date(2004, 4, 5), 'Female', 'Active')
    ]
    student_map = {}
    for uname, sname, semail, sphone, sreg, sdept, scourse, ssem, sdob, sgen, sstat in student_specs:
        u = User.query.filter_by(username=uname).first()
        if not u:
            u = User(username=uname, email=semail, role='student', full_name=sname, is_active_account=True)
            u.set_password('student123')
            db.session.add(u)
            db.session.flush()

        st = Student.query.filter_by(user_id=u.id).first()
        if not st:
            st = Student(
                user_id=u.id,
                register_no=sreg,
                name=sname,
                email=semail,
                phone=sphone,
                address='12 Anna Salai, Main Tech Campus, Chennai',
                department_id=dept_map[sdept].id,
                course_id=course_map[scourse].id,
                admission_year=2024,
                current_semester=ssem,
                academic_year_id=ay_curr.id,
                date_of_birth=sdob,
                gender=sgen,
                enrollment_status=sstat
            )
            db.session.add(st)
            db.session.flush()
        student_map[uname] = st

    # 10. Parent Account (Linked to Arun Kumar)
    parent_user = User.query.filter_by(username='parent_kumar').first()
    if not parent_user:
        parent_user = User(
            username='parent_kumar',
            email='rajesh.kumar@parent.smartmark.edu',
            role='parent',
            full_name='Mr. Rajesh Kumar',
            is_active_account=True
        )
        parent_user.set_password('parent123')
        db.session.add(parent_user)
        db.session.flush()

    arun_st = student_map['student_arun']
    plink = ParentStudent.query.filter_by(parent_user_id=parent_user.id, student_id=arun_st.id).first()
    if not plink:
        plink = ParentStudent(parent_user_id=parent_user.id, student_id=arun_st.id, relationship='Father')
        db.session.add(plink)

    # 11. Populate Marks for Students in Semester 4 Subjects
    # High-achieving marks for Arun Kumar (O and A+ grades)
    arun_marks_data = [
        ('CS401', 36.0, 52.0, 'approved'), # 88% -> A+
        ('CS402', 38.0, 54.0, 'approved'), # 92% -> O
        ('CS403', 35.0, 50.0, 'approved'), # 85% -> A+
        ('CS404', 37.0, 53.0, 'approved'), # 90% -> O
        ('CS405', 48.0, 47.0, 'approved')  # 95% -> O
    ]
    for scode, internal, external, status in arun_marks_data:
        subj = subject_map[scode]
        m = Mark.query.filter_by(student_id=arun_st.id, subject_id=subj.id, examination_id=exam_sem4.id).first()
        if not m:
            m = Mark(
                student_id=arun_st.id,
                subject_id=subj.id,
                examination_id=exam_sem4.id,
                internal_marks=internal * 0.7,
                assignment_marks=internal * 0.3,
                practical_marks=0.0 if subj.subject_type == 'Theory' else internal,
                external_marks=external,
                status=status,
                entered_by_id=faculty_map['faculty_cs'].user_id,
                approved_by_id=admin_user.id,
                remarks='Exemplary academic understanding demonstrated.'
            )
            m.calculate_results()
            db.session.add(m)

    # Varied marks for other students
    cse_subjects = ['CS401', 'CS402', 'CS403', 'CS404', 'CS405']
    other_students = [student_map[k] for k in ['student_priya', 'student_vikram', 'student_deepa', 'student_karthik']]
    for st_obj in other_students:
        for scode in cse_subjects:
            subj = subject_map[scode]
            m = Mark.query.filter_by(student_id=st_obj.id, subject_id=subj.id, examination_id=exam_sem4.id).first()
            if not m:
                # Generate realistic scores between 55 and 95
                rand_total = random.uniform(58, 92)
                internal = round(rand_total * 0.38, 1)
                external = round(rand_total * 0.62, 1)
                m = Mark(
                    student_id=st_obj.id,
                    subject_id=subj.id,
                    examination_id=exam_sem4.id,
                    internal_marks=round(internal * 0.7, 1),
                    assignment_marks=round(internal * 0.3, 1),
                    practical_marks=round(internal * 0.2, 1) if subj.subject_type == 'Practical' else 0.0,
                    external_marks=external,
                    status='approved',
                    entered_by_id=faculty_map['faculty_cs'].user_id,
                    approved_by_id=admin_user.id
                )
                m.calculate_results()
                db.session.add(m)

    # Also add IT student marks (Rahul & Sneha)
    it_subjects = ['IT401', 'IT402']
    it_students = [student_map['student_rahul'], student_map['student_sneha']]
    for st_obj in it_students:
        for scode in it_subjects:
            subj = subject_map[scode]
            m = Mark.query.filter_by(student_id=st_obj.id, subject_id=subj.id, examination_id=exam_sem4.id).first()
            if not m:
                rand_total = random.uniform(65, 88)
                m = Mark(
                    student_id=st_obj.id,
                    subject_id=subj.id,
                    examination_id=exam_sem4.id,
                    internal_marks=round(rand_total * 0.35, 1),
                    assignment_marks=round(rand_total * 0.05, 1),
                    external_marks=round(rand_total * 0.60, 1),
                    status='approved',
                    entered_by_id=faculty_map['faculty_it'].user_id,
                    approved_by_id=admin_user.id
                )
                m.calculate_results()
                db.session.add(m)

    # 12. Attendance Records (Last 30 Days)
    today = date.today()
    for day_offset in range(1, 26):
        att_date = today - timedelta(days=day_offset)
        # Skip weekends
        if att_date.weekday() >= 5:
            continue
        
        # Attendance for Arun Kumar in CS401 (95% attendance)
        s_dbms = subject_map['CS401']
        status = 'Present' if day_offset not in (10, 19) else 'Absent'
        if not AttendanceRecord.query.filter_by(student_id=arun_st.id, subject_id=s_dbms.id, date=att_date).first():
            att = AttendanceRecord(
                student_id=arun_st.id,
                subject_id=s_dbms.id,
                date=att_date,
                status=status,
                recorded_by_id=faculty_map['faculty_cs'].user_id
            )
            db.session.add(att)

        # Attendance for Priya & Vikram
        for s_key in ['student_priya', 'student_vikram']:
            st_temp = student_map[s_key]
            st_status = 'Present' if random.random() > 0.1 else 'Absent'
            if not AttendanceRecord.query.filter_by(student_id=st_temp.id, subject_id=s_dbms.id, date=att_date).first():
                att = AttendanceRecord(
                    student_id=st_temp.id,
                    subject_id=s_dbms.id,
                    date=att_date,
                    status=st_status,
                    recorded_by_id=faculty_map['faculty_cs'].user_id
                )
                db.session.add(att)

    # 13. College Announcements
    announcement_specs = [
        (
            'Semester 4 Final Examination Results Published',
            'The Controller of Examinations has officially approved and published the Semester 4 Final Examination results. Students can view their statement of grades and download official mark sheets from their student portals.',
            'All',
            'Urgent',
            admin_user.id
        ),
        (
            'Faculty Academic Council Meeting Scheduled for Friday',
            'All department Heads and senior faculty members are requested to attend the upcoming Academic Council Meeting in the Senate Hall at 2:30 PM.',
            'Faculty',
            'Important',
            super_admin_user.id
        ),
        (
            'Mandatory Attendance Criteria Reminder (Min 75%)',
            'Students are reminded that a minimum of 75% overall attendance is mandatory to maintain eligibility for end-semester laboratory and theoretical examinations.',
            'Students',
            'Normal',
            admin_user.id
        ),
        (
            'Annual SmartMark TechSymposium 2026 Registrations Open',
            'Department of Computer Science & Engineering is organizing the Annual National Tech Symposium. Paper submissions and project registrations are now open on the college portal.',
            'All',
            'Normal',
            super_admin_user.id
        )
    ]
    for atitle, acontent, atarget, aprio, apub_id in announcement_specs:
        if not Announcement.query.filter_by(title=atitle).first():
            ann = Announcement(
                title=atitle,
                content=acontent,
                target_audience=atarget,
                priority=aprio,
                published_by_id=apub_id,
                is_active=True
            )
            db.session.add(ann)

    # 14. Initial Audit Logs
    audit_specs = [
        (admin_user.id, 'DATABASE_SEED', 'Initialised institutional database with demo curriculum, departments, faculty, and students.'),
        (super_admin_user.id, 'SYSTEM_CONFIG', 'Configured active academic year 2025-2026 and minimum attendance threshold (75%).'),
        (faculty_map['faculty_cs'].user_id, 'MARKS_SUBMIT', 'Submitted Semester 4 Database Management Systems marks for administrative review.'),
        (admin_user.id, 'MARKS_PUBLISH', 'Approved and published Semester 4 examination results for Computer Science & Engineering.')
    ]
    for uid, act, desc in audit_specs:
        if not AuditLog.query.filter_by(action=act).first():
            log = AuditLog(user_id=uid, action=act, description=desc, ip_address='127.0.0.1')
            db.session.add(log)

    db.session.commit()
    print("Database seeding completed successfully!")
