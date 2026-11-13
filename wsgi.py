import os
import sys

basedir = os.path.abspath(os.path.dirname(__file__))
smartmark_dir = os.path.join(basedir, 'smartmark')
if smartmark_dir not in sys.path:
    sys.path.insert(0, smartmark_dir)

from app import app, db, init_db

with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run()

