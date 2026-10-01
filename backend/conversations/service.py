from datetime import datetime
from backend.database.mongodb import get_database
from backend.utils.helpers import generate_uuid, format_timestamp

def create_conversation(participant1_id: str, participant2_id: str) -> dict:
    db = get_database()
    # Check if conversation already exists
    existing = db.conversations.find_one({
        'participants': {'$all': [participant1_id, participant2_id]}
    })
    if existing:
        existing['_id'] = str(existing.get('_id', ''))
        return existing
    
    conv_id = f'CHAT{str(db.conversations.count_documents({}) + 1).zfill(3)}'
    now = datetime.utcnow()
    conv_doc = {
        'conversation_id': conv_id,
        'participants': [participant1_id, participant2_id],
        'created_at': now,
        'updated_at': now,
        'last_message_at': now,
        'status': 'active'
    }
    db.conversations.insert_one(conv_doc)
    conv_doc.pop('_id', None)
    return conv_doc

def get_user_conversations(user_id: str, user_role: str) -> list:
    db = get_database()
    conversations = list(db.conversations.find({'participants': user_id}))
    result = []
    for conv in conversations:
        conv_data = {
            'conversation_id': conv['conversation_id'],
            'participants': conv['participants'],
            'created_at': format_timestamp(conv.get('created_at')),
            'updated_at': format_timestamp(conv.get('updated_at')),
            'last_message_at': format_timestamp(conv.get('last_message_at')),
            'status': conv.get('status', 'active')
        }
        # Add contact info
        other_id = [p for p in conv['participants'] if p != user_id]
        if other_id:
            other_user = db.users.find_one({'_id': other_id[0]})
            if other_user:
                conv_data['contact_name'] = other_user.get('name', 'Unknown')
                conv_data['contact_id'] = other_user['_id']
                conv_data['contact_status'] = other_user.get('status', 'offline')
                conv_data['contact_last_active'] = format_timestamp(other_user.get('last_active'))
        
        # Last message
        last_msg = db.messages.find_one(
            {'conversation_id': conv['conversation_id']},
            sort=[('timestamp', -1)]
        )
        if last_msg:
            conv_data['last_message'] = last_msg.get('content', '')[:50]
        else:
            conv_data['last_message'] = ''
        
        # Unread count
        unread = db.messages.count_documents({
            'conversation_id': conv['conversation_id'],
            'receiver_id': user_id,
            'delivery_status': {'$ne': 'read'}
        })
        conv_data['unread_count'] = unread
        result.append(conv_data)
    
    return result

def get_conversation(conversation_id: str) -> dict:
    db = get_database()
    conv = db.conversations.find_one({'conversation_id': conversation_id})
    if not conv:
        return None
    conv.pop('_id', None)
    return conv

def verify_participant(conversation_id: str, user_id: str) -> bool:
    db = get_database()
    conv = db.conversations.find_one({'conversation_id': conversation_id, 'participants': user_id})
    return conv is not None
