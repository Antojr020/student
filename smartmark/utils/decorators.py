from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user

def role_required(*roles):
    """
    Decorator to restrict access to users with specified roles.
    Super admin automatically inherits all admin privileges.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            
            allowed = False
            for role in roles:
                if current_user.has_role(role):
                    allowed = True
                    break
            
            if not allowed:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def super_admin_required(f):
    return role_required('super_admin')(f)

def admin_required(f):
    return role_required('super_admin', 'admin')(f)

def faculty_required(f):
    return role_required('super_admin', 'admin', 'faculty')(f)

def student_required(f):
    return role_required('student')(f)

def parent_required(f):
    return role_required('parent')(f)
