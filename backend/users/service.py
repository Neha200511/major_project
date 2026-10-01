from backend.database.mongodb import get_database
from backend.utils.helpers import format_user

def get_user_contacts(user_id: str, user_role: str) -> list:
    db = get_database()
    if user_role == 'CHILD':
        conversations = list(db.conversations.find({'participants': user_id}))
        contact_ids = []
        for conv in conversations:
            for p in conv['participants']:
                if p != user_id:
                    contact_ids.append(p)
        contacts = []
        for cid in contact_ids:
            user = db.users.find_one({'_id': cid})
            if user:
                contacts.append(format_user(user))
        return contacts
    elif user_role == 'CONTACT':
        conversations = list(db.conversations.find({'participants': user_id}))
        contact_ids = []
        for conv in conversations:
            for p in conv['participants']:
                if p != user_id:
                    contact_ids.append(p)
        contacts = []
        for cid in contact_ids:
            user = db.users.find_one({'_id': cid})
            if user:
                contacts.append(format_user(user))
        return contacts
    return []

def get_user_profile(user_id: str) -> dict:
    db = get_database()
    user = db.users.find_one({'_id': user_id})
    return format_user(user)
