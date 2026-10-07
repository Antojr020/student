# SmartMark – Student Marks Management System
**"Manage. Analyze. Improve."**

A complete, production-style web application for college administrators, faculty, and students to manage marks, calculate CGPA/SGPA, and securely generate performance PDFs.

## Tech Stack
- **Backend**: Python, Flask, Flask-SQLAlchemy, Flask-Login
- **Frontend**: HTML5, Bootstrap 5, Chart.js
- **Database**: SQLite (SQLAlchemy ORM configured for easy migration to MySQL)
- **APIs**: RandomUser.me API for generating robust sample students on-demand.
- **Tools**: ReportLab for PDF Mark Sheet generation.

## Features Developed
- **Authentication & RBAC**: Admin, Faculty, and Student roles securely implemented using Werkzeug hash verification.
- **SGPA & CGPA Engine**: Centralized 10-point grade logic with automated total verification.
- **ReportLab Mark Sheets**: Export semester performance natively into downloadable PDFs.
- **Dashboard Analytics**: Integrated Chart.js visualizations for pass/fail analytics.
- **Public API Integration**: Pull completely generated student mock-profiles asynchronously and import them into the system database seamlessly.
- **Dark Mode**: Fully implemented aesthetic dark mode overriding Bootstrap native layers.

## Installation & Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize Database**
   This command creates the SQLite database and generates the root Admin user (`admin` / `admin123`).
   ```bash
   flask --app app.py initdb
   ```

3. **Run Application**
   ```bash
   flask --app app.py run
   ```

4. **Access UI**
   - Open browser: `http://127.0.0.1:5000`
   - Test Login: `admin` / `admin123`
