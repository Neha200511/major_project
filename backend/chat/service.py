from datetime import datetime
from backend.database.mongodb import get_database
from backend.utils.helpers import generate_uuid, format_timestamp

def save_message(conversation_id: str, sender_id: str, receiver_id: str, content: str) -> dict:
    db = get_database()
    msg_id = generate_uuid()
    now = datetime.utcnow()
    message_doc = {
        'message_id': msg_id,
        'conversation_id': conversation_id,
        'sender_id': sender_id,
        'receiver_id': receiver_id,
        'content': content,
        'timestamp': now,
        'message_type': 'text',
        'delivery_status': 'sent'
    }
    db.messages.insert_one(message_doc)
    # Update conversation last_message_at
    db.conversations.update_one(
        {'conversation_id': conversation_id},
        {'$set': {'last_message_at': now, 'updated_at': now}}
    )
    message_doc.pop('_id', None)
    message_doc['timestamp'] = format_timestamp(now)
    return message_doc

def mark_messages_read(conversation_id: str, user_id: str) -> int:
    db = get_database()
    result = db.messages.update_many(
        {'conversation_id': conversation_id, 'receiver_id': user_id, 'delivery_status': {'$ne': 'read'}},
        {'$set': {'delivery_status': 'read'}}
    )
    return result.modified_count

def get_unread_count(conversation_id: str, user_id: str) -> int:
    db = get_database()
    return db.messages.count_documents({
        'conversation_id': conversation_id,
        'receiver_id': user_id,
        'delivery_status': {'$ne': 'read'}
    })
