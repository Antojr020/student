import os
import random
import requests
from flask import Flask, render_template, redirect, url_for, request, jsonify, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db
from models.user import User
from models.core import Student, Faculty, Subject, Mark, AuditLog
from utils.grading import calculate_grade_and_points, calculate_sgpa, calculate_cgpa
from utils.pdf import generate_marksheet_pdf

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def log_action(user_id, action, desc):
    log = AuditLog(user_id=user_id, action=action, description=desc)
    db.session.add(log)
    db.session.commit()

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin': return redirect(url_for('admin_dashboard'))
        elif current_user.role == 'faculty': return redirect(url_for('faculty_dashboard'))
        else: return redirect(url_for('student_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            log_action(user.id, "LOGIN", "User logged in")
            return redirect(url_for('index'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    log_action(current_user.id, "LOGOUT", "User logged out")
    logout_user()
    return redirect(url_for('login'))

# ----- ADMIN ROUTES -----
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin': return "Forbidden", 403
    stats = {
        'total_students': Student.query.count(),
        'total_faculty': Faculty.query.count(),
        'total_subjects': Subject.query.count()
    }
    return render_template('admin/dashboard.html', stats=stats)

@app.route('/api/generate_samples', methods=['POST'])
@login_required
def generate_samples():
    if current_user.role != 'admin': return jsonify({"error": "Forbidden"}), 403
    try:
        # Fetch data from Random User API
        res = requests.get('https://randomuser.me/api/?results=5')
        data = res.json()['results']
        for p in data:
            # Create user account for student
            u = User(username=p['login']['username'], role='student')
            u.set_password('password123')
            db.session.add(u)
            db.session.flush()
            
            # Create student record
            s = Student(
                user_id=u.id,
                register_no=f"25PCA{random.randint(1000, 9999)}",
                name=f"{p['name']['first']} {p['name']['last']}",
                email=p['email'],
                phone=p['phone'],
                department="Computer Applications",
                programme="MCA",
                year=1,
                semester=1,
                gender=p['gender'].capitalize(),
                profile_image=p['picture']['large']
            )
            db.session.add(s)
        db.session.commit()
        log_action(current_user.id, "IMPORT_STUDENTS", "Generated sample students from API")
        return jsonify({"message": "Successfully imported 5 sample students from RandomUser API."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/students')
@login_required
def get_students():
    students = Student.query.all()
    return jsonify([{'register_no': s.register_no, 'name': s.name, 'department': s.department} for s in students])

# ----- FACULTY ROUTES -----
@app.route('/faculty/dashboard')
@login_required
def faculty_dashboard():
    if current_user.role != 'faculty': return "Forbidden", 403
    return render_template('faculty/dashboard.html', faculty=current_user.faculty)

# ----- STUDENT ROUTES -----
@app.route('/student/dashboard')
@login_required
def student_dashboard():
    if current_user.role != 'student': return "Forbidden", 403
    student = current_user.student
    marks = student.marks.all()
    sgpa = calculate_sgpa(marks)
    cgpa = calculate_cgpa(student)
    return render_template('student/dashboard.html', student=student, marks=marks, sgpa=sgpa, cgpa=cgpa)

@app.route('/download/marksheet/<int:student_id>/<int:semester>')
@login_required
def download_marksheet(student_id, semester):
    student = Student.query.get_or_404(student_id)
    # Ensure students can only download their own mark sheet
    if current_user.role == 'student' and current_user.student.id != student.id:
        return "Forbidden", 403
        
    marks = student.marks.all()
    sgpa = calculate_sgpa(marks)
    cgpa = calculate_cgpa(student)
    
    pdf = generate_marksheet_pdf(student, marks, sgpa, cgpa)
    return send_file(pdf, download_name=f"{student.register_no}_Marksheet.pdf", as_attachment=True)

# ----- CLI SETUP -----
@app.cli.command('initdb')
def initdb_command():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('Database initialized. Admin user created: admin / admin123')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
