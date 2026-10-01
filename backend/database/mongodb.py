from pymongo import MongoClient, ASCENDING, DESCENDING
from backend.config.settings import settings

_client = None
_db = None

def get_client():
    global _client
    if _client is None:
        _client = MongoClient(settings.MONGODB_URI)
    return _client

def get_database():
    global _db
    if _db is None:
        client = get_client()
        _db = client.get_default_database() if '/' in settings.MONGODB_URI and settings.MONGODB_URI.rsplit('/', 1)[-1] else client['childsafe']
    return _db

def create_indexes():
    db = get_database()
    # Users indexes
    db.users.create_index([('email', ASCENDING)], unique=True)
    db.users.create_index([('role', ASCENDING)])
    # Messages indexes
    db.messages.create_index([('conversation_id', ASCENDING), ('timestamp', ASCENDING)])
    db.messages.create_index([('sender_id', ASCENDING)])
    # Conversations indexes
    db.conversations.create_index([('participants', ASCENDING)])
    db.conversations.create_index([('conversation_id', ASCENDING)], unique=True)
    # Risk scores indexes
    db.risk_scores.create_index([('conversation_id', ASCENDING), ('timestamp', DESCENDING)])
    # Alerts indexes
    db.alerts.create_index([('child_id', ASCENDING), ('status', ASCENDING)])
    db.alerts.create_index([('conversation_id', ASCENDING)])
    # Behaviour profiles
    db.behaviour_profiles.create_index([('conversation_id', ASCENDING)], unique=True)
    # Audit logs
    db.audit_logs.create_index([('timestamp', DESCENDING)])
    # Parent-child links
    db.parent_child_links.create_index([('parent_id', ASCENDING)])
    db.parent_child_links.create_index([('child_id', ASCENDING)])
    print('Database indexes created successfully')
