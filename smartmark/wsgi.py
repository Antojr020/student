"""WSGI entry point for production deployment (gunicorn / Render / Railway)."""
from app import app, db, init_db

# Initialize database tables and seed on first deploy
with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run()
