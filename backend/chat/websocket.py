import json
import asyncio
import traceback
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from backend.auth.security import decode_token
from backend.database.mongodb import get_database
from backend.chat.service import save_message, mark_messages_read, get_unread_count
from backend.conversations.service import verify_participant, get_conversation
from backend.utils.helpers import format_timestamp, sanitize_input
from backend.auth.service import update_user_status

# Try to import monitoring engine
try:
    from backend.monitoring.risk_engine import RiskEngine
    _risk_engine_available = True
except ImportError:
    _risk_engine_available = False

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        self._lock = asyncio.Lock()
    
    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            # Close existing connection if any
            if user_id in self.active_connections:
                try:
                    await self.active_connections[user_id].close()
                except Exception:
                    pass
            self.active_connections[user_id] = websocket
        update_user_status(user_id, 'online')
    
    async def disconnect(self, user_id: str):
        async with self._lock:
            self.active_connections.pop(user_id, None)
        update_user_status(user_id, 'offline')
    
    async def send_personal(self, user_id: str, data: dict):
        async with self._lock:
            ws = self.active_connections.get(user_id)
        if ws:
            try:
                await ws.send_json(data)
            except Exception:
                await self.disconnect(user_id)
    
    async def broadcast_status(self, user_id: str, status: str, relevant_users: list):
        for uid in relevant_users:
            await self.send_personal(uid, {
                'type': 'status',
                'user_id': user_id,
                'status': status
            })
    
    def get_online_users(self) -> list:
        return list(self.active_connections.keys())
    
    def is_online(self, user_id: str) -> bool:
        return user_id in self.active_connections

manager = ConnectionManager()

# Parent alert connections
parent_connections: dict[str, WebSocket] = {}

def _get_risk_engine():
    if _risk_engine_available:
        db = get_database()
        return RiskEngine(db)
    return None

def _get_relevant_users(user_id: str) -> list:
    db = get_database()
    convs = list(db.conversations.find({'participants': user_id}))
    users = set()
    for c in convs:
        for p in c['participants']:
            if p != user_id:
                users.add(p)
    return list(users)

async def websocket_endpoint(websocket: WebSocket, token: str):
    payload = decode_token(token)
    if not payload:
        await websocket.close(code=4001, reason='Invalid token')
        return
    
    user_id = payload.get('sub')
    if not user_id:
        await websocket.close(code=4001, reason='Invalid token')
        return
    
    db = get_database()
    user = db.users.find_one({'_id': user_id})
    if not user:
        await websocket.close(code=4001, reason='User not found')
        return
    
    await manager.connect(user_id, websocket)
    
    # Broadcast online status
    relevant = _get_relevant_users(user_id)
    await manager.broadcast_status(user_id, 'online', relevant)
    
    # Send online users list to the connecting user
    online_list = [uid for uid in relevant if manager.is_online(uid)]
    await manager.send_personal(user_id, {
        'type': 'online_users',
        'users': online_list
    })
    
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg_data = json.loads(data)
            except json.JSONDecodeError:
                continue
            
            msg_type = msg_data.get('type', '')
            conversation_id = msg_data.get('conversation_id', '')
            
            if msg_type == 'message':
                content = sanitize_input(msg_data.get('content', ''))
                if not content or not conversation_id:
                    continue
                
                # Verify sender is participant
                if not verify_participant(conversation_id, user_id):
                    continue
                
                # Get receiver
                conv = get_conversation(conversation_id)
                if not conv:
                    continue
                receiver_id = [p for p in conv['participants'] if p != user_id]
                if not receiver_id:
                    continue
                receiver_id = receiver_id[0]
                
                # Save message
                message_doc = save_message(conversation_id, user_id, receiver_id, content)
                
                # Send to sender (confirmation)
                await manager.send_personal(user_id, {
                    'type': 'message',
                    'message': message_doc
                })
                
                # Send to receiver
                await manager.send_personal(receiver_id, {
                    'type': 'message',
                    'message': message_doc
                })
                
                # Send unread count to receiver
                unread = get_unread_count(conversation_id, receiver_id)
                await manager.send_personal(receiver_id, {
                    'type': 'unread_count',
                    'conversation_id': conversation_id,
                    'count': unread
                })
                
                # Async risk analysis (don't block chat)
                asyncio.create_task(_analyze_message(message_doc, conversation_id, user_id))
            
            elif msg_type == 'typing':
                if conversation_id and verify_participant(conversation_id, user_id):
                    conv = get_conversation(conversation_id)
                    if conv:
                        for p in conv['participants']:
                            if p != user_id:
                                await manager.send_personal(p, {
                                    'type': 'typing',
                                    'conversation_id': conversation_id,
                                    'user_id': user_id
                                })
            
            elif msg_type == 'read':
                if conversation_id and verify_participant(conversation_id, user_id):
                    count = mark_messages_read(conversation_id, user_id)
                    if count > 0:
                        conv = get_conversation(conversation_id)
                        if conv:
                            for p in conv['participants']:
                                if p != user_id:
                                    await manager.send_personal(p, {
                                        'type': 'read',
                                        'conversation_id': conversation_id,
                                        'user_id': user_id
                                    })
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f'WebSocket error for {user_id}: {e}')
        traceback.print_exc()
    finally:
        await manager.disconnect(user_id)
        await manager.broadcast_status(user_id, 'offline', relevant)

async def _analyze_message(message_doc: dict, conversation_id: str, sender_id: str):
    """Run risk analysis asynchronously after message delivery."""
    try:
        risk_engine = _get_risk_engine()
        if not risk_engine:
            return
        
        result = await risk_engine.analyze_message(message_doc, conversation_id)
        
        if result and result.get('should_alert', False):
            alert_data = result.get('alert_data')
            if alert_data:
                # Save alert to DB
                db = get_database()
                db.alerts.insert_one(alert_data.copy())
                
                # Notify parent via WebSocket
                await _notify_parent(alert_data)
    except Exception as e:
        print(f'Risk analysis error: {e}')
        traceback.print_exc()

async def _notify_parent(alert_data: dict):
    """Send alert notification to connected parent."""
    db = get_database()
    child_id = alert_data.get('child_id')
    if not child_id:
        return
    
    link = db.parent_child_links.find_one({'child_id': child_id})
    if not link:
        return
    
    parent_id = link['parent_id']
    
    # Try parent alert WebSocket first
    if parent_id in parent_connections:
        try:
            ws = parent_connections[parent_id]
            # Serialize datetime fields
            safe_alert = {}
            for k, v in alert_data.items():
                if k == '_id':
                    continue
                if isinstance(v, datetime):
                    safe_alert[k] = v.isoformat()
                else:
                    safe_alert[k] = v
            await ws.send_json({'type': 'alert', 'alert': safe_alert})
        except Exception:
            parent_connections.pop(parent_id, None)
    
    # Also try regular WebSocket
    await manager.send_personal(parent_id, {
        'type': 'alert',
        'alert': {
            'alert_id': alert_data.get('alert_id', ''),
            'severity': alert_data.get('severity', ''),
            'risk_score': alert_data.get('risk_score', 0),
            'contact_name': alert_data.get('contact_name', ''),
            'categories': alert_data.get('categories', []),
            'reasons': alert_data.get('reasons', [])[:3],
            'created_at': format_timestamp(alert_data.get('created_at'))
        }
    })
