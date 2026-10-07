from fastapi import APIRouter, Depends, HTTPException, status
from backend.auth.security import get_current_user
from backend.conversations.service import (
    create_conversation, get_user_conversations, 
    get_conversation, verify_participant
)
from backend.database.models import ConversationCreate
from backend.database.mongodb import get_database
from backend.utils.helpers import format_timestamp

router = APIRouter(prefix='/api', tags=['Conversations'])

@router.post('/conversations')
async def create_conv(data: ConversationCreate, current_user: dict = Depends(get_current_user)):
    conv = create_conversation(current_user['_id'], data.participant_id)
    return {'conversation': conv}

@router.get('/conversations')
async def get_conversations(current_user: dict = Depends(get_current_user)):
    conversations = get_user_conversations(current_user['_id'], current_user['role'])
    return {'conversations': conversations}

@router.get('/conversations/{conversation_id}')
async def get_conv(conversation_id: str, current_user: dict = Depends(get_current_user)):
    if not verify_participant(conversation_id, current_user['_id']):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Access denied')
    conv = get_conversation(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail='Conversation not found')
    db = get_database()
    other_id = [p for p in conv.get('participants', []) if p != current_user['_id']]
    if other_id:
        other_user = db.users.find_one({'_id': other_id[0]})
        if other_user:
            conv['contact_name'] = other_user.get('name', 'Unknown')
            conv['contact_id'] = other_user['_id']
            conv['contact_status'] = other_user.get('status', 'offline')
    return {'conversation': conv}

@router.get('/messages/{conversation_id}')
async def get_messages(conversation_id: str, limit: int = 50, offset: int = 0, current_user: dict = Depends(get_current_user)):
    # For parent role, check if they are linked to the child in this conversation
    if current_user['role'] == 'PARENT':
        db = get_database()
        link = db.parent_child_links.find_one({'parent_id': current_user['_id']})
        if link:
            conv = get_conversation(conversation_id)
            if conv and link['child_id'] not in conv.get('participants', []):
                raise HTTPException(status_code=403, detail='Access denied')
        else:
            raise HTTPException(status_code=403, detail='No linked child found')
    else:
        if not verify_participant(conversation_id, current_user['_id']):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Access denied')
    
    db = get_database()
    messages = list(
        db.messages.find({'conversation_id': conversation_id})
        .sort('timestamp', 1)
        .skip(offset)
        .limit(limit)
    )
    result = []
    for msg in messages:
        result.append({
            'message_id': msg.get('message_id', ''),
            'conversation_id': msg.get('conversation_id', ''),
            'sender_id': msg.get('sender_id', ''),
            'receiver_id': msg.get('receiver_id', ''),
            'content': msg.get('content', ''),
            'timestamp': format_timestamp(msg.get('timestamp')),
            'message_type': msg.get('message_type', 'text'),
            'delivery_status': msg.get('delivery_status', 'sent')
        })
    total = db.messages.count_documents({'conversation_id': conversation_id})
    return {'messages': result, 'total': total}
