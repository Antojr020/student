import unittest
from app import app
from models import db, User, Student, Faculty, Subject, Mark, Examination

class SmartMarkTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def login(self, username, password):
        self.logout()
        return self.client.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)

    # 1. Authentication Tests
    def test_invalid_login(self):
        res = self.login('admin', 'wrong_password')
        self.assertIn(b"Invalid username or password", res.data)

    def test_super_admin_login(self):
        res = self.login('superadmin', 'Password@123')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Collegiate Administration Dashboard", res.data)

    def test_admin_login(self):
        res = self.login('admin', 'admin123')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Collegiate Administration Dashboard", res.data)

    def test_faculty_login(self):
        res = self.login('faculty_cs', 'faculty123')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Faculty Academic Portal", res.data)

    def test_student_login(self):
        res = self.login('student_arun', 'student123')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Student Academic Portal", res.data)

    def test_parent_login(self):
        res = self.login('parent_kumar', 'parent123')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Ward Academic Progress Overview", res.data)

    # 2. RBAC Security Tests
    def test_student_cannot_access_admin_dashboard(self):
        self.login('student_arun', 'student123')
        res = self.client.get('/admin/dashboard')
        self.assertEqual(res.status_code, 403)

    def test_student_cannot_access_faculty_portal(self):
        self.login('student_arun', 'student123')
        res = self.client.get('/faculty/dashboard')
        self.assertEqual(res.status_code, 403)

    def test_student_cannot_download_other_student_pdf(self):
        self.login('student_arun', 'student123')
        with app.app_context():
            priya = Student.query.filter_by(register_no='2024CSE002').first()
            priya_id = priya.id if priya else 2
        res = self.client.get(f'/download/marksheet/{priya_id}/4')
        self.assertEqual(res.status_code, 403)

    # 3. Admin Views Tests
    def test_admin_views(self):
        self.login('admin', 'admin123')
        
        # Students directory
        res = self.client.get('/admin/students')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Student Information Management", res.data)

        # Faculty directory
        res = self.client.get('/admin/faculty')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Faculty & Academic Staff Directory", res.data)

        # Academic Structure
        res = self.client.get('/admin/departments-courses')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Academic Structure & Curriculum", res.data)

        # Examinations
        res = self.client.get('/admin/examinations')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Examinations & Assessment Management", res.data)

        # Marks Approval
        res = self.client.get('/admin/marks-approval')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Faculty Marks Verification", res.data)

        # Attendance
        res = self.client.get('/admin/attendance')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Collegiate Attendance Overview", res.data)

        # Announcements
        res = self.client.get('/admin/announcements')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Campus Announcements", res.data)

        # Reports
        res = self.client.get('/admin/reports')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Honour Roll", res.data)

        # Audit Logs
        res = self.client.get('/admin/audit-logs')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"System & Security Audit Trail", res.data)

    # 4. Data Export Tests
    def test_csv_exports(self):
        self.login('admin', 'admin123')
        
        res_st = self.client.get('/admin/students/export')
        self.assertEqual(res_st.status_code, 200)
        self.assertEqual(res_st.mimetype, 'text/csv')
        self.assertIn(b"Register No,Name,Department", res_st.data)

        res_att = self.client.get('/admin/attendance/export')
        self.assertEqual(res_att.status_code, 200)
        self.assertEqual(res_att.mimetype, 'text/csv')
        self.assertIn(b"Register No,Student Name,Department", res_att.data)

    # 5. Student Marksheet & PDF Generation Tests
    def test_student_official_marksheet_pdf(self):
        self.login('student_arun', 'student123')
        with app.app_context():
            arun = Student.query.filter_by(register_no='2024CSE001').first()
            arun_id = arun.id
            sem = arun.current_semester

        # Marksheet HTML View
        res_html = self.client.get('/student/marksheet')
        self.assertEqual(res_html.status_code, 200)
        self.assertIn(b"OFFICIAL STATEMENT OF GRADES & MARKS", res_html.data)

        # Marksheet Download PDF
        res_pdf = self.client.get(f'/download/marksheet/{arun_id}/{sem}')
        self.assertEqual(res_pdf.status_code, 200)
        self.assertEqual(res_pdf.mimetype, 'application/pdf')
        self.assertTrue(res_pdf.data.startswith(b'%PDF-'))

    # 6. Faculty Marks Entry and Admin Approval Workflow
    def test_marks_entry_and_approval_workflow(self):
        with app.app_context():
            subj = Subject.query.filter_by(subject_code='CS401').first()
            exam = Examination.query.first()
            arun = Student.query.filter_by(register_no='2024CSE001').first()
            existing_mark = Mark.query.filter_by(student_id=arun.id, subject_id=subj.id, examination_id=exam.id).first()
            if existing_mark:
                existing_mark.status = 'draft'
                db.session.commit()
            subj_id = subj.id
            exam_id = exam.id
            arun_id = arun.id

        # Step 1: Faculty logs in and submits marks
        self.login('faculty_cs', 'faculty123')

        res_submit = self.client.post('/faculty/marks/save', data={
            'subject_id': subj_id,
            'examination_id': exam_id,
            'action': 'submit',
            'student_ids': [str(arun_id)],
            f'internal_{arun_id}': '35',
            f'external_{arun_id}': '55'
        }, follow_redirects=True)
        self.assertEqual(res_submit.status_code, 200)

        # Step 2: Verify mark is in submitted status
        with app.app_context():
            mark = Mark.query.filter_by(student_id=arun_id, subject_id=subj_id, examination_id=exam_id).first()
            self.assertEqual(mark.status, 'submitted')
            self.assertEqual(mark.total_marks, 90.0)
            self.assertEqual(mark.grade, 'O')
            mark_id = mark.id

        # Step 3: Admin logs in and approves mark
        self.login('admin', 'admin123')
        res_approve = self.client.post(f'/admin/marks/approve/{mark_id}', follow_redirects=True)
        self.assertEqual(res_approve.status_code, 200)

        # Step 4: Verify mark is now approved
        with app.app_context():
            mark_approved = db.session.get(Mark, mark_id)
            self.assertEqual(mark_approved.status, 'approved')

    # 7. Attendance Recording Workflow
    def test_attendance_recording_workflow(self):
        self.login('faculty_cs', 'faculty123')
        with app.app_context():
            subj = Subject.query.filter_by(subject_code='CS401').first()
            arun = Student.query.filter_by(register_no='2024CSE001').first()
            subj_id, arun_id = subj.id, arun.id

        res = self.client.post('/faculty/attendance/save', data={
            'subject_id': subj_id,
            'date': '2026-10-20',
            'student_ids': [str(arun_id)],
            f'status_{arun_id}': 'Present',
            f'remarks_{arun_id}': 'Active class participation'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # Student checks attendance
        self.login('student_arun', 'student123')
        res_att = self.client.get('/student/attendance')
        self.assertEqual(res_att.status_code, 200)
        self.assertIn(b"My Attendance History", res_att.data)

    # 8. Student Age Calculation Test
    def test_student_age_calculation(self):
        with app.app_context():
            arun = Student.query.filter_by(register_no='2024CSE001').first()
            self.assertIsNotNone(arun.age)
            self.assertGreaterEqual(arun.age, 18)

if __name__ == '__main__':
    unittest.main()

