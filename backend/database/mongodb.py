import logging
import os
import pickle
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

PERSIST_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data')
PERSIST_FILE = os.path.join(PERSIST_DIR, 'db_storage.pkl')
COLLECTIONS = ['users', 'conversations', 'messages', 'risk_scores', 'alerts', 'behaviour_profiles', 'audit_logs', 'parent_child_links']

def save_mock_db():
    """Persist in-memory database collections to disk so messages and history survive restarts."""
    if not _is_mock or _db is None:
        return
    try:
        os.makedirs(PERSIST_DIR, exist_ok=True)
        dump = {}
        for coll in COLLECTIONS:
            dump[coll] = list(_db[coll].find())
        with open(PERSIST_FILE, 'wb') as f:
            pickle.dump(dump, f)
    except Exception as e:
        logger.error("Failed to persist database to disk: %s", str(e))

def load_mock_db() -> bool:
    """Load persisted database collections from disk if available."""
    if not _is_mock or _db is None or not os.path.exists(PERSIST_FILE):
        return False
    try:
        with open(PERSIST_FILE, 'rb') as f:
            dump = pickle.load(f)
        if dump and isinstance(dump, dict):
            has_data = False
            for coll, docs in dump.items():
                if docs:
                    has_data = True
                    _db[coll].delete_many({})
                    _db[coll].insert_many(docs)
            if has_data:
                print(f'Loaded persistent chat database from {PERSIST_FILE}')
                return True
    except Exception as e:
        logger.error("Failed to load persistent database from disk: %s", str(e))
    return False

def auto_seed_if_needed():
    db = get_database()
    if _is_mock:
        if load_mock_db():
            return
    if db.users.count_documents({}) == 0:
        print('Database is empty. Auto-seeding demo accounts and conversations...')
        try:
            from scripts.seed_data import seed
            seed()
            save_mock_db()
        except Exception as err:
            print(f'Auto-seed error: {err}')


