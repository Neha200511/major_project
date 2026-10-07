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
    """
    Tracks every open WebSocket per user. A user may have several tabs/devices
    open at once, so each user maps to a SET of sockets. A user is considered
    offline only when their last socket closes.
    """

    def __init__(self):
        self.active_connections: dict[str, set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, user_id: str, websocket: WebSocket) -> bool:
        """Register a socket. Returns True if this is the user's first socket (came online)."""
        await websocket.accept()
        async with self._lock:
            sockets = self.active_connections.setdefault(user_id, set())
            first = len(sockets) == 0
            sockets.add(websocket)
        update_user_status(user_id, 'online')
        return first

    async def disconnect(self, user_id: str, websocket: WebSocket) -> bool:
        """Remove a socket. Returns True if the user has no sockets left (went offline)."""
        async with self._lock:
            sockets = self.active_connections.get(user_id)
            if sockets is None:
                return False
            sockets.discard(websocket)
            if sockets:
                return False
            self.active_connections.pop(user_id, None)
        update_user_status(user_id, 'offline')
        return True

    async def send_personal(self, user_id: str, data: dict):
        """Send to every open socket for a user (all their tabs)."""
        async with self._lock:
            sockets = list(self.active_connections.get(user_id, set()))
        dead = []
        for ws in sockets:
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            await self.disconnect(user_id, ws)

    async def broadcast_status(self, user_id: str, status: str, relevant_users: list):
        for uid in relevant_users:
            await self.send_personal(uid, {
                'type': 'status',
                'user_id': user_id,
                'status': status,
            })

    def get_online_users(self) -> list:
        return list(self.active_connections.keys())

    def is_online(self, user_id: str) -> bool:
        return bool(self.active_connections.get(user_id))


manager = ConnectionManager()

# Parent alert connections
parent_connections: dict[str, WebSocket] = {}

# Load the risk engine (and its ML model) once, not on every message
_risk_engine_instance = None


def _get_risk_engine():
    global _risk_engine_instance
    if not _risk_engine_available:
        return None
    if _risk_engine_instance is None:
        _risk_engine_instance = RiskEngine(get_database())
    return _risk_engine_instance


def _get_relevant_users(user_id: str) -> list:
    """Users who share a conversation with this user (and the linked parent)."""
    db = get_database()
    users = set()
    for c in db.conversations.find({'participants': user_id}):
        for p in c['participants']:
            if p != user_id:
                users.add(p)
    return list(users)


def _other_participant(conv: dict, user_id: str):
    others = [p for p in conv.get('participants', []) if p != user_id]
    return others[0] if others else None


async def websocket_endpoint(websocket: WebSocket, token: str):
    payload = decode_token(token)
    if not payload or not payload.get('sub'):
        await websocket.close(code=4001, reason='Invalid token')
        return

    user_id = payload['sub']
    db = get_database()
    if not db.users.find_one({'_id': user_id}):
        await websocket.close(code=4001, reason='User not found')
        return

    came_online = await manager.connect(user_id, websocket)
    relevant = _get_relevant_users(user_id)

    # Tell this user's contacts that they are online
    if came_online:
        await manager.broadcast_status(user_id, 'online', relevant)

        # Messages that were waiting for this user are now delivered (grey double tick)
        pending = db.messages.distinct(
            'conversation_id', {'receiver_id': user_id, 'delivery_status': 'sent'}
        )
        if pending:
            db.messages.update_many(
                {'receiver_id': user_id, 'delivery_status': 'sent'},
                {'$set': {'delivery_status': 'delivered'}},
            )
            for cid in pending:
                conv = get_conversation(cid)
                sender = _other_participant(conv, user_id) if conv else None
                if sender:
                    await manager.send_personal(sender, {
                        'type': 'delivered',
                        'conversation_id': cid,
                        'user_id': user_id,
                    })

    # Send the list of contacts who are currently online to this socket
    try:
        await websocket.send_json({
            'type': 'online_users',
            'users': [uid for uid in relevant if manager.is_online(uid)],
        })
    except Exception:
        pass

    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg_data = json.loads(data)
            except json.JSONDecodeError:
                continue

            msg_type = msg_data.get('type', '')
            conversation_id = msg_data.get('conversation_id', '')

            if msg_type == 'ping':
                await websocket.send_json({'type': 'pong'})
                continue

            if msg_type == 'message':
                content = sanitize_input(msg_data.get('content', ''))
                client_id = msg_data.get('client_id')
                if not content or not conversation_id:
                    continue
                if not verify_participant(conversation_id, user_id):
                    continue
                conv = get_conversation(conversation_id)
                if not conv:
                    continue
                receiver_id = _other_participant(conv, user_id)
                if not receiver_id:
                    continue

                # 1. Persist
                message_doc = save_message(conversation_id, user_id, receiver_id, content)

                # 2. If the receiver is connected, it is delivered right away
                if manager.is_online(receiver_id):
                    db.messages.update_one(
                        {'message_id': message_doc['message_id']},
                        {'$set': {'delivery_status': 'delivered'}},
                    )
                    message_doc['delivery_status'] = 'delivered'

                # 3. Deliver to the receiver and echo to all of the sender's tabs
                await manager.send_personal(receiver_id, {'type': 'message', 'message': message_doc})
                await manager.send_personal(user_id, {
                    'type': 'message',
                    'message': message_doc,
                    'client_id': client_id,
                })

                # 4. Unread badge for the receiver
                await manager.send_personal(receiver_id, {
                    'type': 'unread_count',
                    'conversation_id': conversation_id,
                    'count': get_unread_count(conversation_id, receiver_id),
                })

                # 5. Risk analysis runs in the background; chat is never blocked
                asyncio.create_task(_analyze_message(message_doc, conversation_id, user_id))

            elif msg_type == 'typing':
                if conversation_id and verify_participant(conversation_id, user_id):
                    conv = get_conversation(conversation_id)
                    other = _other_participant(conv, user_id) if conv else None
                    if other:
                        await manager.send_personal(other, {
                            'type': 'typing',
                            'conversation_id': conversation_id,
                            'user_id': user_id,
                        })

            elif msg_type == 'read':
                if conversation_id and verify_participant(conversation_id, user_id):
                    count = mark_messages_read(conversation_id, user_id)
                    # Reset this user's own unread badge in all their tabs
                    await manager.send_personal(user_id, {
                        'type': 'unread_count',
                        'conversation_id': conversation_id,
                        'count': 0,
                    })
                    if count > 0:
                        conv = get_conversation(conversation_id)
                        other = _other_participant(conv, user_id) if conv else None
                        if other:
                            # Sender sees blue double ticks
                            await manager.send_personal(other, {
                                'type': 'read',
                                'conversation_id': conversation_id,
                                'user_id': user_id,
                            })

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f'WebSocket error for {user_id}: {e}')
        traceback.print_exc()
    finally:
        went_offline = await manager.disconnect(user_id, websocket)
        if went_offline:
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
                db = get_database()
                db.alerts.insert_one(alert_data.copy())
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

    safe_alert = {}
    for k, v in alert_data.items():
        if k == '_id':
            continue
        safe_alert[k] = v.isoformat() if isinstance(v, datetime) else v

    # Dedicated parent alert socket
    if parent_id in parent_connections:
        try:
            await parent_connections[parent_id].send_json({'type': 'alert', 'alert': safe_alert})
            return
        except Exception:
            parent_connections.pop(parent_id, None)

    # Fallback: parent's regular chat socket
    await manager.send_personal(parent_id, {'type': 'alert', 'alert': safe_alert})
