import os
import shutil
import tempfile
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

# Serverless environment detection (Vercel, AWS Lambda) where filesystems are read-only
is_serverless = (
    os.environ.get('VERCEL') == '1' or
    os.environ.get('AWS_LAMBDA_FUNCTION_NAME') is not None or
    bool(os.environ.get('NOW_REGION'))
)

if is_serverless:
    instance_path = os.path.join(tempfile.gettempdir(), 'instance')
    os.makedirs(instance_path, exist_ok=True)
    default_sqlite_db = os.path.join(instance_path, 'smartmark.db').replace('\\', '/')
    repo_db = os.path.join(basedir, 'instance', 'smartmark.db')
    target_db = os.path.join(instance_path, 'smartmark.db')
    if os.path.exists(repo_db) and not os.path.exists(target_db):
        try:
            shutil.copy2(repo_db, target_db)
        except Exception:
            pass
else:
    try:
        instance_path = os.path.join(basedir, 'instance')
        os.makedirs(instance_path, exist_ok=True)
        default_sqlite_db = os.path.join(instance_path, 'smartmark.db').replace('\\', '/')
    except OSError:
        # Graceful fallback if host filesystem is read-only
        instance_path = os.path.join(tempfile.gettempdir(), 'instance')
        os.makedirs(instance_path, exist_ok=True)
        default_sqlite_db = os.path.join(instance_path, 'smartmark.db').replace('\\', '/')


# Resolve database URL/URI flexibly for SQLite, PostgreSQL, MySQL
raw_db_url = os.environ.get('DATABASE_URL') or os.environ.get('DATABASE_URI')

if not raw_db_url or raw_db_url.strip() in ('sqlite:///smartmark.db', 'sqlite://smartmark.db', 'sqlite:///instance/smartmark.db'):
    # Default to absolute path in instance/ to prevent cwd / read-only directory issues in WSGI / PythonAnywhere
    database_uri = f'sqlite:///{default_sqlite_db}'
elif raw_db_url.startswith('postgres://'):
    # Fix SQLAlchemy 1.4+ compatibility (Render, Supabase, Heroku postgres:// URLs) using psycopg2
    database_uri = raw_db_url.replace('postgres://', 'postgresql+psycopg2://', 1)
elif raw_db_url.startswith('postgresql://') and not raw_db_url.startswith('postgresql+'):
    # Ensure psycopg2-binary driver is targeted directly in SQLAlchemy 2.0
    database_uri = raw_db_url.replace('postgresql://', 'postgresql+psycopg2://', 1)
elif raw_db_url.startswith('sqlite:///') and not raw_db_url.startswith('sqlite:////') and not (len(raw_db_url) > 11 and raw_db_url[11] == ':'):
    # Relative SQLite path: resolve against basedir
    rel_path = raw_db_url[len('sqlite:///'):]
    abs_path = os.path.join(basedir, rel_path).replace('\\', '/')
    database_uri = f'sqlite:///{abs_path}'
else:
    database_uri = raw_db_url

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-production-key-change-me'
    SQLALCHEMY_DATABASE_URI = database_uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Production Engine Options: pre-ping to detect stale connections and connection timeouts
    if database_uri.startswith('sqlite:'):
        SQLALCHEMY_ENGINE_OPTIONS = {
            'connect_args': {'timeout': 30, 'check_same_thread': False},
            'pool_pre_ping': True,
        }
    else:
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_pre_ping': True,
            'pool_recycle': 280,
        }



