import os
import sys

# Ensure repository root and smartmark directory are on Python sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
smartmark_dir = os.path.join(root_dir, 'smartmark')

for directory in [root_dir, smartmark_dir]:
    if directory not in sys.path:
        sys.path.insert(0, directory)

from app import app

# Vercel serverless functions load 'app' as the WSGI application callable
