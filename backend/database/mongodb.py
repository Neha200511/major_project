import logging
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from backend.config.settings import settings

logger = logging.getLogger(__name__)

_client = None
_db = None
_is_mock = False

def get_client():
    global _client, _is_mock
    if _client is None:
        try:
            client = MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=2000)
            client.admin.command('ping')
            _client = client
            _is_mock = False
            print(f'Connected to MongoDB at {settings.MONGODB_URI}')
        except Exception as e:
            print(f'Warning: MongoDB connection failed ({e}). Falling back to in-memory mongomock.')
            try:
                import mongomock
                _client = mongomock.MongoClient()
                _is_mock = True
            except ImportError:
                raise e
    return _client

def get_database():
    global _db
    if _db is None:
        client = get_client()
        if _is_mock:
            _db = client['childsafe']
        else:
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

def auto_seed_if_needed():
    db = get_database()
    if db.users.count_documents({}) == 0:
        print('Database is empty. Auto-seeding demo accounts and conversations...')
        try:
            from scripts.seed_data import seed
            seed()
        except Exception as err:
            print(f'Auto-seed error: {err}')

