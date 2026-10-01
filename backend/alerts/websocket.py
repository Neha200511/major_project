import json
from fastapi import WebSocket, WebSocketDisconnect
from backend.auth.security import decode_token
from backend.database.mongodb import get_database
from backend.chat.websocket import parent_connections

async def alerts_websocket_endpoint(websocket: WebSocket, token: str):
    payload = decode_token(token)
    if not payload:
        await websocket.close(code=4001, reason='Invalid token')
        return
    
    user_id = payload.get('sub')
    user_role = payload.get('role', '')
    
    if user_role != 'PARENT':
        await websocket.close(code=4003, reason='Parents only')
        return
    
    await websocket.accept()
    parent_connections[user_id] = websocket
    
    try:
        while True:
            data = await websocket.receive_text()
            # Parent WebSocket is primarily for receiving alerts
            # But can handle ping/pong for keepalive
            try:
                msg = json.loads(data)
                if msg.get('type') == 'ping':
                    await websocket.send_json({'type': 'pong'})
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        parent_connections.pop(user_id, None)
