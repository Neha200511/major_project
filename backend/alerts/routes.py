from fastapi import APIRouter, Depends, HTTPException
from backend.auth.security import get_current_user, require_role
from backend.alerts.service import (
    get_alerts, get_alert_by_id, acknowledge_alert, resolve_alert,
    get_conversation_risk_summary, get_risk_trends
)
from backend.conversations.service import get_user_conversations
from backend.database.mongodb import get_database
from backend.utils.helpers import format_timestamp, get_severity
from backend.config.settings import settings
from datetime import datetime

router = APIRouter(prefix='/api', tags=['Parent Dashboard'])

def _get_child_id(parent_id: str) -> str:
    db = get_database()
    link = db.parent_child_links.find_one({'parent_id': parent_id})
    if not link:
        return None
    return link['child_id']

@router.get('/parent/overview')
async def parent_overview(current_user: dict = Depends(require_role('PARENT'))):
    child_id = _get_child_id(current_user['_id'])
    if not child_id:
        raise HTTPException(status_code=404, detail='No linked child found')
    
    db = get_database()
    conversations = list(db.conversations.find({'participants': child_id}))
    
    open_alerts = db.alerts.count_documents({'child_id': child_id, 'status': {'$in': ['NEW', 'VIEWED']}})
    
    # Calculate risk per conversation
    high_risk_count = 0
    total_risk = 0
    conv_count = len(conversations)
    
    for conv in conversations:
        risk = get_conversation_risk_summary(conv['conversation_id'])
        if risk['risk_score'] >= 60:
            high_risk_count += 1
        total_risk += risk['risk_score']
    
    avg_risk = total_risk / max(conv_count, 1)
    
    if avg_risk <= 29:
        safety_status = 'SAFE'
    elif avg_risk <= 59:
        safety_status = 'ATTENTION'
    else:
        safety_status = 'HIGH RISK'
    
    return {
        'safety_status': safety_status,
        'active_conversations': conv_count,
        'open_alerts': open_alerts,
        'high_risk_contacts': high_risk_count,
        'overall_risk_score': round(avg_risk, 1)
    }

@router.get('/parent/conversations')
async def parent_conversations(current_user: dict = Depends(require_role('PARENT'))):
    child_id = _get_child_id(current_user['_id'])
    if not child_id:
        raise HTTPException(status_code=404, detail='No linked child found')
    
    db = get_database()
    conversations = list(db.conversations.find({'participants': child_id}))
    
    result = []
    for conv in conversations:
        contact_id = [p for p in conv['participants'] if p != child_id]
        contact_name = 'Unknown'
        if contact_id:
            contact = db.users.find_one({'_id': contact_id[0]})
            if contact:
                contact_name = contact.get('name', 'Unknown')
            contact_id = contact_id[0]
        else:
            contact_id = ''
        
        risk = get_conversation_risk_summary(conv['conversation_id'])
        msg_count = db.messages.count_documents({'conversation_id': conv['conversation_id']})
        
        result.append({
            'conversation_id': conv['conversation_id'],
            'contact_name': contact_name,
            'contact_id': contact_id,
            'risk_score': risk['risk_score'],
            'severity': risk['severity'],
            'categories': risk.get('categories', {}),
            'last_message_at': format_timestamp(conv.get('last_message_at')),
            'message_count': msg_count
        })
    
    return {'conversations': result}

@router.get('/parent/alerts')
async def parent_alerts(
    status: str = 'all', severity: str = 'all',
    current_user: dict = Depends(require_role('PARENT'))
):
    child_id = _get_child_id(current_user['_id'])
    if not child_id:
        raise HTTPException(status_code=404, detail='No linked child found')
    alerts = get_alerts(child_id, status, severity)
    return {'alerts': alerts}

@router.get('/parent/alerts/{alert_id}')
async def parent_alert_detail(alert_id: str, current_user: dict = Depends(require_role('PARENT'))):
    alert = get_alert_by_id(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail='Alert not found')
    return {'alert': alert}

@router.patch('/parent/alerts/{alert_id}/acknowledge')
async def ack_alert(alert_id: str, current_user: dict = Depends(require_role('PARENT'))):
    alert = acknowledge_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail='Alert not found')
    from backend.auth.service import create_audit_log
    create_audit_log(current_user['_id'], 'ALERT_ACKNOWLEDGED', f'Alert {alert_id} acknowledged')
    return {'alert': alert}

@router.patch('/parent/alerts/{alert_id}/resolve')
async def res_alert(alert_id: str, current_user: dict = Depends(require_role('PARENT'))):
    alert = resolve_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail='Alert not found')
    from backend.auth.service import create_audit_log
    create_audit_log(current_user['_id'], 'ALERT_RESOLVED', f'Alert {alert_id} resolved')
    return {'alert': alert}

@router.get('/parent/risk/{conversation_id}')
async def conversation_risk(conversation_id: str, current_user: dict = Depends(require_role('PARENT'))):
    risk = get_conversation_risk_summary(conversation_id)
    return risk

@router.get('/parent/trends/{conversation_id}')
async def conversation_trends(conversation_id: str, current_user: dict = Depends(require_role('PARENT'))):
    trends = get_risk_trends(conversation_id)
    return trends

@router.get('/parent/settings')
async def get_parent_settings(current_user: dict = Depends(require_role('PARENT'))):
    return {
        'risk_weights': settings.RISK_WEIGHTS,
        'risk_thresholds': settings.RISK_THRESHOLDS,
        'alert_cooldown_minutes': settings.ALERT_COOLDOWN_MINUTES
    }

@router.get('/parent/reports')
async def get_reports(current_user: dict = Depends(require_role('PARENT'))):
    child_id = _get_child_id(current_user['_id'])
    if not child_id:
        raise HTTPException(status_code=404, detail='No linked child found')
    
    db = get_database()
    conversations = list(db.conversations.find({'participants': child_id}))
    
    total_messages = 0
    total_alerts = db.alerts.count_documents({'child_id': child_id})
    conv_summaries = []
    
    for conv in conversations:
        msg_count = db.messages.count_documents({'conversation_id': conv['conversation_id']})
        total_messages += msg_count
        risk = get_conversation_risk_summary(conv['conversation_id'])
        contact_id = [p for p in conv['participants'] if p != child_id]
        contact_name = 'Unknown'
        if contact_id:
            contact = db.users.find_one({'_id': contact_id[0]})
            if contact:
                contact_name = contact.get('name', 'Unknown')
        conv_summaries.append({
            'conversation_id': conv['conversation_id'],
            'contact_name': contact_name,
            'message_count': msg_count,
            'risk_score': risk['risk_score'],
            'severity': risk['severity']
        })
    
    # Category distribution across all alerts
    all_alerts = list(db.alerts.find({'child_id': child_id}))
    category_dist = {}
    for alert in all_alerts:
        for cat in alert.get('categories', []):
            category_dist[cat] = category_dist.get(cat, 0) + 1
    
    return {
        'total_messages': total_messages,
        'total_alerts': total_alerts,
        'conversations': conv_summaries,
        'category_distribution': category_dist,
        'generated_at': format_timestamp()
    }

@router.get('/dev/status')
async def dev_status(current_user: dict = Depends(get_current_user)):
    if settings.ENVIRONMENT != 'development':
        raise HTTPException(status_code=403, detail='Only available in development mode')
    
    db = get_database()
    from backend.chat.websocket import manager
    
    # ML model status
    ml_status = {'loaded': False, 'metrics': {}}
    try:
        from backend.monitoring.ml_model import MLClassifier
        clf = MLClassifier()
        ml_status['loaded'] = clf.is_loaded
        ml_status['metrics'] = clf.get_metrics()
    except Exception:
        pass
    
    return {
        'connected_users': len(manager.get_online_users()),
        'online_users': manager.get_online_users(),
        'total_messages': db.messages.count_documents({}),
        'total_conversations': db.conversations.count_documents({}),
        'total_alerts': db.alerts.count_documents({}),
        'total_users': db.users.count_documents({}),
        'ml_model': ml_status,
        'database_status': 'connected',
        'environment': settings.ENVIRONMENT
    }
