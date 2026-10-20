from flask import request
from models import db, AuditLog

def log_action(user_id, action, description, ip_address=None):
    """
    Log sensitive academic and administrative actions into the audit log.
    """
    try:
        if not ip_address:
            try:
                ip_address = request.remote_addr
            except Exception:
                ip_address = '127.0.0.1'
                
        log = AuditLog(
            user_id=user_id,
            action=action,
            description=description,
            ip_address=ip_address
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # Non-critical failure should not crash main request
        print(f"Failed to record audit log: {e}")
