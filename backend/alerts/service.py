from datetime import datetime, timedelta
from backend.database.mongodb import get_database
from backend.config.settings import settings
from backend.utils.helpers import generate_uuid, format_timestamp, get_severity

def create_alert(alert_data: dict) -> dict:
    db = get_database()
    # Check cooldown
    if check_alert_cooldown(alert_data.get('conversation_id', '')):
        return None
    
    if 'alert_id' not in alert_data:
        alert_data['alert_id'] = generate_uuid()
    if 'created_at' not in alert_data:
        alert_data['created_at'] = datetime.utcnow()
    if 'status' not in alert_data:
        alert_data['status'] = 'NEW'
    
    db.alerts.insert_one(alert_data.copy())
    from backend.database.mongodb import save_mock_db
    save_mock_db()
    return alert_data

def get_alerts(child_id: str, status_filter: str = None, severity_filter: str = None) -> list:
    db = get_database()
    query = {'child_id': child_id}
    if status_filter and status_filter != 'all':
        query['status'] = status_filter.upper()
    if severity_filter and severity_filter != 'all':
        query['severity'] = severity_filter.upper()
    
    alerts = list(db.alerts.find(query).sort('created_at', -1))
    result = []
    for alert in alerts:
        alert.pop('_id', None)
        if isinstance(alert.get('created_at'), datetime):
            alert['created_at'] = format_timestamp(alert['created_at'])
        if isinstance(alert.get('acknowledged_at'), datetime):
            alert['acknowledged_at'] = format_timestamp(alert['acknowledged_at'])
        result.append(alert)
    return result

def get_alert_by_id(alert_id: str) -> dict:
    db = get_database()
    alert = db.alerts.find_one({'alert_id': alert_id})
    if alert:
        alert.pop('_id', None)
        if isinstance(alert.get('created_at'), datetime):
            alert['created_at'] = format_timestamp(alert['created_at'])
        if isinstance(alert.get('acknowledged_at'), datetime):
            alert['acknowledged_at'] = format_timestamp(alert['acknowledged_at'])
    return alert

def acknowledge_alert(alert_id: str) -> dict:
    db = get_database()
    db.alerts.update_one(
        {'alert_id': alert_id},
        {'$set': {'status': 'ACKNOWLEDGED', 'acknowledged_at': datetime.utcnow()}}
    )
    from backend.database.mongodb import save_mock_db
    save_mock_db()
    return get_alert_by_id(alert_id)

def resolve_alert(alert_id: str) -> dict:
    db = get_database()
    db.alerts.update_one(
        {'alert_id': alert_id},
        {'$set': {'status': 'RESOLVED', 'acknowledged_at': datetime.utcnow()}}
    )
    from backend.database.mongodb import save_mock_db
    save_mock_db()
    return get_alert_by_id(alert_id)

def check_alert_cooldown(conversation_id: str) -> bool:
    db = get_database()
    cooldown_time = datetime.utcnow() - timedelta(minutes=settings.ALERT_COOLDOWN_MINUTES)
    recent = db.alerts.find_one({
        'conversation_id': conversation_id,
        'created_at': {'$gte': cooldown_time},
        'status': {'$in': ['NEW', 'VIEWED']}
    })
    return recent is not None

def get_conversation_risk_summary(conversation_id: str) -> dict:
    db = get_database()
    latest_risk = db.risk_scores.find_one(
        {'conversation_id': conversation_id},
        sort=[('timestamp', -1)]
    )
    if not latest_risk:
        return {
            'risk_score': 0, 'severity': 'SAFE',
            'categories': {}, 'layer_scores': {},
            'reasons': []
        }
    latest_risk.pop('_id', None)
    return {
        'risk_score': latest_risk.get('risk_score', 0),
        'severity': latest_risk.get('severity', 'SAFE'),
        'categories': latest_risk.get('categories', {}),
        'layer_scores': {
            'rule': latest_risk.get('rule_score', 0),
            'ml': latest_risk.get('ml_score', 0),
            'context': latest_risk.get('context_score', 0),
            'behaviour': latest_risk.get('behaviour_score', 0),
            'llm': latest_risk.get('llm_score', 0)
        },
        'reasons': latest_risk.get('reasons', [])
    }

def get_risk_trends(conversation_id: str) -> dict:
    db = get_database()
    # Get behaviour profile
    profile = db.behaviour_profiles.find_one({'conversation_id': conversation_id})
    if not profile:
        return {
            'risk_history': [],
            'trend': 'new',
            'average_risk': 0,
            'category_frequency': {}
        }
    return {
        'risk_history': profile.get('risk_history', [])[-50:],
        'trend': profile.get('trend', 'stable'),
        'average_risk': profile.get('average_risk', 0),
        'category_frequency': profile.get('category_frequency', {})
    }
