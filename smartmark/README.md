# SmartMark — Professional College Management System (CMS)
> **"Manage. Analyze. Improve."** — An Enterprise-Grade Institutional Academic & Administrative ERP Suite.

---

## 1. Project Overview

**SmartMark CMS** is a complete, database-driven College Management System designed to meet the operational, examination, and governance demands of modern collegiate and university institutions. 

Built on a robust Python/Flask and SQLAlchemy relational architecture, SmartMark delivers a unified multi-portal experience with dedicated interfaces for **Super Administrators**, **College Administrators**, **Faculty Members**, **Students**, and **Parents**.

---

## 2. Key Modules & Functional Architecture

### A. Multiple Role-Based Portals & Authentication
* **Super Administrator**: Complete governance over users, departments, courses, curricula, grading policies, audit logs, and institutional system settings.
* **College Administrator**: Daily academic operations, student enrollments, faculty directory, examination schedules, mark approval & publication, and attendance analytics.
* **Faculty & Staff Portal**: Assigned course dashboard, spreadsheet-style batch marks evaluation, daily class attendance recording, and class performance analytics.
* **Student Academic Portal**: Personalized academic dashboard, semester marks breakdown, visual performance charts, attendance tracking with eligibility indicators, official marksheet viewer, and ReportLab PDF download.
* **Parent Portal**: Secure view-only access to ward's academic marks, SGPA/CGPA standings, attendance rates, and official report cards.

### B. Student Information Management
* Comprehensive student profiles: Unique Registration Number, Age dynamically calculated from Date of Birth, gender, contact details, residential address, department, degree programme, semester level, and enrollment status.
* Live search, multi-parameter filtering (by department, semester, enrollment status), and pagination.
* CSV Import: Bulk enrollment of students via standard CSV files.
* CSV Export: Export authorized student directories.
* Archive / Soft-delete workflows for student records.

### C. Academic Structure Administration
* **Departments**: Code, name, HOD details, and mission descriptions.
* **Degree Courses**: Degree types (Undergraduate, Postgraduate, Diploma), duration, total semester cycles.
* **Academic Years & Semesters**: Multi-year management with active session indicators.
* **Curriculum Subjects**: Theory, Practical, Elective, and Project courses with credits, max internal/external marks, and pass cutoffs.

### D. Examination, Marks Entry & Verification Workflow
* **Configurable Assessment Types**: Internal Assessment 1 (IA-1), Internal Assessment 2 (IA-2), Model Examinations, Practical Laboratories, and End-Semester University Examinations.
* **Faculty Marks Evaluation**: Interactive marks entry with real-time automatic client-side & server-side score validation and letter grade calculation.
* **Multi-Stage Workflow**:
  1. *Draft*: Saved by faculty for ongoing revisions.
  2. *Submitted*: Forwarded to Academic Administration for verification.
  3. *Approved / Published*: Verified by Controller of Examinations and released to student marksheets. Once approved, marks are locked against unauthorized modifications.
* **Academic Calculation Engine**:
  * 10-Point UGC / University grading scale: **O** (90–100%), **A+** (80–89%), **A** (70–79%), **B+** (60–69%), **B** (50–59%), **C** (40–49%), and **RA** (< 40% Re-appear / Arrear).
  * Weighted **SGPA** (Semester Grade Point Average) and **CGPA** (Cumulative Grade Point Average) computed automatically across all registered credits.

### E. Official Marksheets & ReportLab PDF Engine
* **Digital Marksheet View**: Official institutional letterhead, student dossier, detailed course marks table, GPA classification, grading legend, and university controller signature blocks.
* **Print-Optimized**: Dedicated `@media print` stylesheet removing headers, sidebars, and screen controls for clean physical printing.
* **Publication-Quality PDF**: Native ReportLab generator with custom canvas layout, tabular borders, NAAC accreditation banner, and downloadable attachment naming.

### F. Attendance Tracking & Shortage Alerts
* Daily and subject-wise attendance recording by authorized faculty.
* Automated percentage calculation per student and per subject.
* **Low Attendance Warning System**: Students falling below the mandatory 75% threshold are flagged with shortage warnings and exam ineligibility notices.
* CSV Export for institutional attendance rosters.

### G. Campus Announcements & Broadcasts
* Target audience routing: Broadcast notices to *All Users*, *Students Only*, or *Faculty Only*.
* Priority levels: *Normal*, *Important*, and *Urgent Alert*.
* Real-time notification pulse and dashboard alert widgets.

### H. Governance, Analytics & Audit Trail
* **Reports Hub**:
  * Dean's Honour Roll (Top performing students).
  * Academic Support Required (Students with RA / arrears).
  * Department-wise enrollment and pass/fail distribution.
  * One-click CSV export for all reporting categories.
* **Audit Logs**: Tamper-evident logging of logins, logouts, marks submissions, marks approvals, password resets, and curriculum alterations.

---

## 3. Technology Stack

* **Backend**: Python 3.12, Flask 3.1, Flask-SQLAlchemy 3.1, Flask-Login 0.6, Werkzeug 3.1
* **Database**: SQLite (SQLAlchemy ORM with foreign keys, constraints, and relational cascades; ready for PostgreSQL / MySQL)
* **Frontend**: Modern Enterprise ERP Design System (Vanilla CSS with custom properties, Bootstrap 5.3, Bootstrap Icons)
* **Visualizations**: Chart.js 4.4 (Live DB-driven donut, bar, and performance charts)
* **Document Generation**: ReportLab 4.5 (Vector PDF Generation)

---

## 4. Default Demo Accounts

For evaluation, the system includes pre-configured demo accounts across all user roles:

| Role | Username | Password | Notes |
|---|---|---|---|
| **Super Admin** | `superadmin` | `Password@123` | Full governance, settings, curriculum, audit logs |
| **College Admin** | `admin` | `admin123` | Academic operations, student enrollments, marks approval |
| **Faculty (CSE HOD)** | `faculty_cs` | `faculty123` | Dr. Alan Turing — DBMS, Algorithms |
| **Faculty (IT)** | `faculty_it` | `faculty123` | Dr. Grace Hopper — Web Systems, Networks |
| **Student** | `student_arun` | `student123` | Arun Kumar (`2024CSE001`) — Semester 4 CSE |
| **Student** | `student_priya` | `student123` | Priya Sharma (`2024CSE002`) — Semester 4 CSE |
| **Parent** | `parent_kumar` | `parent123` | Mr. Rajesh Kumar (Linked to Arun Kumar) |

> **Tip**: The login page features **One-Click Demo Credentials** buttons to instantly test and switch between roles without typing.

---

## 5. Installation & Setup Instructions

### 1. Prerequisites
* Python 3.10, 3.11, or 3.12 installed on your system.
* pip package manager.

### 2. Install Required Dependencies
Open terminal in the project directory (`smartmark/`) and run:
```bash
pip install -r requirements.txt
```

### 3. Initialize Database & Seed Demo Data
To initialize the SQLite database schema and populate complete collegiate data (departments, courses, faculty, students, marks, attendance, announcements):
```bash
python seed.py
```
*(Or alternatively run `flask --app app.py initdb`)*

### 4. Run the Application
Start the Flask development server:
```bash
python app.py
```
The application will launch at:
```
http://127.0.0.1:5000/
```

---

## 6. Running Automated Tests

A comprehensive unit and integration test suite (`test_app.py`) is included to verify all core workflows, authentication, role-based access control, marks approval, attendance, and PDF generation.

To run the test suite:
```bash
python test_app.py
```

Expected output:
```
Ran 15 tests in ~1.9s
OK
```

---

## 7. Security Architecture

1. **Password Hashing**: Passwords stored using Werkzeug secure PBKDF2/SHA256 salted hashes.
2. **Strict RBAC & Resource Validation**:
   * Students can strictly access only their personal dossiers, marks, and attendance.
   * Faculty can only evaluate students and enter marks for subjects officially allocated to them.
   * Parents can only view progress for their explicitly linked wards.
   * Unpublished exam results are strictly hidden from students until administratively approved.
3. **Audit Trail**: All administrative and examination actions automatically generate audit records with user identification, action codes, IP address, and timestamps.
4. **Export Safeguards**: CSV and PDF export endpoints validate session roles before rendering streaming responses.

---

## 8. License & Attribution
Developed for **SmartMark Institute of Technology & Science**. All rights reserved.
