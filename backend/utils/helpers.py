import uuid
from datetime import datetime
from backend.config.settings import settings

def generate_uuid() -> str:
    return uuid.uuid4().hex[:24]

def get_severity(score: float) -> str:
    if score <= settings.RISK_THRESHOLDS['safe']:
        return 'SAFE'
    elif score <= settings.RISK_THRESHOLDS['moderate']:
        return 'MODERATE'
    elif score <= settings.RISK_THRESHOLDS['high']:
        return 'HIGH'
    else:
        return 'CRITICAL'

def format_timestamp(dt=None) -> str:
    if dt is None:
        dt = datetime.utcnow()
    if isinstance(dt, str):
        return dt
    return dt.isoformat() + 'Z'

def sanitize_input(text: str) -> str:
    if not text:
        return ''
    text = text.strip()
    text = text[:5000]  # Max length
    return text

def format_user(user_doc: dict) -> dict:
    if not user_doc:
        return None
    return {
        '_id': str(user_doc.get('_id', '')),
        'name': user_doc.get('name', ''),
        'email': user_doc.get('email', ''),
        'role': user_doc.get('role', ''),
        'avatar': user_doc.get('avatar'),
        'created_at': format_timestamp(user_doc.get('created_at')),
        'last_active': format_timestamp(user_doc.get('last_active')),
        'status': user_doc.get('status', 'offline')
    }
