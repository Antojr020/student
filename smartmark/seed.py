import os
import shutil
from app import app
from models import db
from utils.seeder import seed_database

if __name__ == '__main__':
    with app.app_context():
        db_path = os.path.join(os.path.dirname(__file__), 'instance', 'smartmark.db')
        if os.path.exists(db_path):
            backup_path = os.path.join(os.path.dirname(__file__), 'instance', 'smartmark.db.bak')
            try:
                shutil.copyfile(db_path, backup_path)
                print(f"Backed up existing database to {backup_path}")
            except Exception as e:
                print(f"Backup notice: {e}")
        
        # Drop and recreate schema with full relational models
        db.drop_all()
        db.create_all()
        print("Created all relational database tables.")
        
        # Seed comprehensive collegiate demo data
        seed_database()
        print("Successfully seeded all institutional data!")
