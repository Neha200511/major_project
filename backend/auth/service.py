from datetime import datetime
from backend.database.mongodb import get_database
from backend.auth.security import hash_password, verify_password
from backend.utils.helpers import generate_uuid, format_timestamp, format_user

def register_user(name: str, email: str, password: str, role: str) -> dict:
    db = get_database()
    existing = db.users.find_one({'email': email})
    if existing:
        return None
    user_id = generate_uuid()
    user_doc = {
        '_id': user_id,
        'name': name,
        'email': email,
        'password_hash': hash_password(password),
        'role': role,
        'avatar': None,
        'created_at': datetime.utcnow(),
        'last_active': datetime.utcnow(),
        'status': 'offline'
    }
    db.users.insert_one(user_doc)
    return format_user(user_doc)

def authenticate_user(email: str, password: str) -> dict:
    db = get_database()
    user = db.users.find_one({'email': email})
    if not user:
        return None
    if not verify_password(password, user['password_hash']):
        return None
    return format_user(user)

def get_user_by_id(user_id: str) -> dict:
    db = get_database()
    user = db.users.find_one({'_id': user_id})
    return format_user(user)

def get_user_by_email(email: str) -> dict:
    db = get_database()
    user = db.users.find_one({'email': email})
    return format_user(user)

def update_user_status(user_id: str, status: str):
    db = get_database()
    db.users.update_one({'_id': user_id}, {'$set': {'status': status, 'last_active': datetime.utcnow()}})

def create_audit_log(user_id: str, action: str, details: str = ''):
    db = get_database()
    db.audit_logs.insert_one({
        'user_id': user_id,
        'action': action,
        'details': details,
        'timestamp': datetime.utcnow()
    })
