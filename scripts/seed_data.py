import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from backend.database.mongodb import get_database, create_indexes
from backend.auth.security import hash_password
from backend.utils.helpers import generate_uuid

def seed():
    db = get_database()
    
    # Clear existing data
    for collection in ['users', 'conversations', 'messages', 'risk_scores', 'alerts', 'behaviour_profiles', 'audit_logs', 'parent_child_links']:
        db[collection].delete_many({})
    
    print('Cleared existing data.')
    create_indexes()
    
    # Create user IDs
    parent_id = 'PARENT001'
    child_id = 'CHILD001'
    alice_id = 'ALICE001'
    bob_id = 'BOB001'
    charlie_id = 'CHARLIE001'
    david_id = 'DAVID001'
    
    password_hash = hash_password('demo123')
    now = datetime.utcnow()
    
    users = [
        {'_id': parent_id, 'name': 'Parent User', 'email': 'parent@example.com', 'password_hash': password_hash, 'role': 'PARENT', 'avatar': None, 'created_at': now, 'last_active': now, 'status': 'offline'},
        {'_id': child_id, 'name': 'Nimai', 'email': 'child@example.com', 'password_hash': password_hash, 'role': 'CHILD', 'avatar': None, 'created_at': now, 'last_active': now, 'status': 'offline'},
        {'_id': alice_id, 'name': 'Alice', 'email': 'alice@example.com', 'password_hash': password_hash, 'role': 'CONTACT', 'avatar': None, 'created_at': now, 'last_active': now, 'status': 'offline'},
        {'_id': bob_id, 'name': 'Bob', 'email': 'bob@example.com', 'password_hash': password_hash, 'role': 'CONTACT', 'avatar': None, 'created_at': now, 'last_active': now, 'status': 'offline'},
        {'_id': charlie_id, 'name': 'Charlie', 'email': 'charlie@example.com', 'password_hash': password_hash, 'role': 'CONTACT', 'avatar': None, 'created_at': now, 'last_active': now, 'status': 'offline'},
        {'_id': david_id, 'name': 'David', 'email': 'david@example.com', 'password_hash': password_hash, 'role': 'CONTACT', 'avatar': None, 'created_at': now, 'last_active': now, 'status': 'offline'},
    ]
    db.users.insert_many(users)
    print(f'Created {len(users)} users.')
    
    # Parent-child link
    db.parent_child_links.insert_one({'parent_id': parent_id, 'child_id': child_id})
    print('Created parent-child link.')
    
    # Create conversations
    conversations = [
        {'conversation_id': 'CHAT001', 'participants': [child_id, alice_id], 'created_at': now, 'updated_at': now, 'last_message_at': now, 'status': 'active'},
        {'conversation_id': 'CHAT002', 'participants': [child_id, bob_id], 'created_at': now, 'updated_at': now, 'last_message_at': now, 'status': 'active'},
        {'conversation_id': 'CHAT003', 'participants': [child_id, charlie_id], 'created_at': now, 'updated_at': now, 'last_message_at': now, 'status': 'active'},
        {'conversation_id': 'CHAT004', 'participants': [child_id, david_id], 'created_at': now, 'updated_at': now, 'last_message_at': now, 'status': 'active'},
    ]
    db.conversations.insert_many(conversations)
    print(f'Created {len(conversations)} conversations.')
    
    # Demo messages
    msg_id = 0
    def make_msg(conv_id, sender, receiver, content, minutes_ago):
        nonlocal msg_id
        msg_id += 1
        return {
            'message_id': f'MSG{str(msg_id).zfill(5)}',
            'conversation_id': conv_id,
            'sender_id': sender,
            'receiver_id': receiver,
            'content': content,
            'timestamp': now - timedelta(minutes=minutes_ago),
            'message_type': 'text',
            'delivery_status': 'read'
        }
    
    messages = [
        # CHAT001 - Child + Alice - SAFE (exam discussion)
        make_msg('CHAT001', alice_id, child_id, 'Hey! How was your exam today?', 120),
        make_msg('CHAT001', child_id, alice_id, 'It was pretty good actually! I think I passed.', 118),
        make_msg('CHAT001', alice_id, child_id, 'That\'s great! What subject?', 115),
        make_msg('CHAT001', child_id, alice_id, 'Computer Networks. The networking questions were easy.', 113),
        make_msg('CHAT001', alice_id, child_id, 'Nice! I have mine tomorrow. So nervous 😅', 110),
        make_msg('CHAT001', child_id, alice_id, 'You\'ll do fine! Did you study the OSI model?', 108),
        make_msg('CHAT001', alice_id, child_id, 'Yeah, I went through all seven layers. TCP/IP too.', 105),
        make_msg('CHAT001', child_id, alice_id, 'Perfect. Good luck! 🍀', 103),
        
        # CHAT002 - Child + Bob - FALSE POSITIVE TEST (movie discussion)
        make_msg('CHAT002', bob_id, child_id, 'Did you watch that new action movie?', 90),
        make_msg('CHAT002', child_id, bob_id, 'Yeah, I watched it last night!', 88),
        make_msg('CHAT002', bob_id, child_id, 'The villain killed everyone in that scene. It was insane!', 85),
        make_msg('CHAT002', child_id, bob_id, 'That scene was crazy! The special effects were amazing.', 83),
        make_msg('CHAT002', bob_id, child_id, 'The hero almost died like three times lol', 80),
        make_msg('CHAT002', child_id, bob_id, 'I know right! We totally killed it watching it in IMAX 😂', 78),
        make_msg('CHAT002', bob_id, child_id, 'The fight scenes were brutal though', 75),
        make_msg('CHAT002', child_id, bob_id, 'Best movie this year for sure!', 73),
        
        # CHAT003 - Child + Charlie - ESCALATION TEST (grooming/secrecy)
        make_msg('CHAT003', charlie_id, child_id, 'Hey, how are you doing?', 200),
        make_msg('CHAT003', child_id, charlie_id, 'I\'m good, thanks! How about you?', 198),
        make_msg('CHAT003', charlie_id, child_id, 'Good! You seem really mature for your age.', 180),
        make_msg('CHAT003', child_id, charlie_id, 'Thanks I guess lol', 178),
        make_msg('CHAT003', charlie_id, child_id, 'Do you have a best friend you trust?', 160),
        make_msg('CHAT003', child_id, charlie_id, 'Yeah, a few close friends.', 158),
        make_msg('CHAT003', charlie_id, child_id, 'That\'s nice. Do your parents check your phone?', 140),
        make_msg('CHAT003', child_id, charlie_id, 'Sometimes, why?', 138),
        make_msg('CHAT003', charlie_id, child_id, 'Just curious. Don\'t tell your parents about our chat.', 120),
        make_msg('CHAT003', child_id, charlie_id, 'Why not?', 118),
        make_msg('CHAT003', charlie_id, child_id, 'They wouldn\'t understand. This is just between us.', 100),
        make_msg('CHAT003', child_id, charlie_id, 'Okay I guess...', 98),
        make_msg('CHAT003', charlie_id, child_id, 'You\'re special, you know that? Can you send me a photo of yourself?', 80),
        make_msg('CHAT003', child_id, charlie_id, 'What kind of photo?', 78),
        make_msg('CHAT003', charlie_id, child_id, 'Just a private one, for me. Keep it our secret.', 60),
        
        # CHAT004 - Child + David - SAFE (sports discussion)
        make_msg('CHAT004', david_id, child_id, 'Did you watch the cricket match yesterday?', 100),
        make_msg('CHAT004', child_id, david_id, 'Yes! What a game!', 98),
        make_msg('CHAT004', david_id, child_id, 'We absolutely killed them in the last over! 🏏', 95),
        make_msg('CHAT004', child_id, david_id, 'That six was insane! The bowler was destroyed!', 93),
        make_msg('CHAT004', david_id, child_id, 'Haha brutal! Want to play cricket this weekend?', 90),
        make_msg('CHAT004', child_id, david_id, 'Definitely! I\'ll bring my bat.', 88),
        make_msg('CHAT004', david_id, child_id, 'Awesome! Let\'s crush the other team! 💪', 85),
        make_msg('CHAT004', child_id, david_id, 'We\'re going to murder them on the pitch 😂', 83),
    ]
    
    db.messages.insert_many(messages)
    print(f'Created {len(messages)} demo messages.')
    
    # Pre-populate Risk Scores & Profiles for Parent Dashboard Demo
    # CHAT001 (Alice - SAFE)
    db.risk_scores.insert_one({
        'risk_id': generate_uuid(),
        'conversation_id': 'CHAT001',
        'message_id': 'MSG00008',
        'risk_score': 8,
        'severity': 'SAFE',
        'categories': {'SAFE': 0.92, 'CYBERBULLYING': 0.05},
        'rule_score': 0,
        'ml_score': 10,
        'context_score': 5,
        'behaviour_score': 5,
        'llm_score': 0,
        'timestamp': now - timedelta(minutes=100),
        'reasons': ['Academic/exam preparation topic detected', 'Normal conversational velocity', 'Positive mutual engagement']
    })
    db.behaviour_profiles.insert_one({
        'conversation_id': 'CHAT001',
        'child_id': child_id,
        'contact_id': alice_id,
        'risk_history': [
            {'score': 5, 'timestamp': (now - timedelta(days=4)).isoformat()},
            {'score': 8, 'timestamp': (now - timedelta(days=3)).isoformat()},
            {'score': 6, 'timestamp': (now - timedelta(days=2)).isoformat()},
            {'score': 7, 'timestamp': (now - timedelta(days=1)).isoformat()},
            {'score': 8, 'timestamp': now.isoformat()},
        ],
        'average_risk': 6.8,
        'trend': 'stable',
        'category_frequency': {'SAFE': 12},
        'last_updated': now
    })

    # CHAT002 (Bob - SAFE - Movie Discussion False Positive Test)
    db.risk_scores.insert_one({
        'risk_id': generate_uuid(),
        'conversation_id': 'CHAT002',
        'message_id': 'MSG00016',
        'risk_score': 12,
        'severity': 'SAFE',
        'categories': {'SAFE': 0.88, 'THREAT': 0.08},
        'rule_score': 10,
        'ml_score': 15,
        'context_score': 8,
        'behaviour_score': 8,
        'llm_score': 0,
        'timestamp': now - timedelta(minutes=70),
        'reasons': [
            'Entertainment/movie context detected - violence terms de-escalated',
            'Casual slang and laughing emojis indicate friendly interaction',
            'Context verified: safe pop culture discussion'
        ]
    })
    db.behaviour_profiles.insert_one({
        'conversation_id': 'CHAT002',
        'child_id': child_id,
        'contact_id': bob_id,
        'risk_history': [
            {'score': 10, 'timestamp': (now - timedelta(days=4)).isoformat()},
            {'score': 12, 'timestamp': (now - timedelta(days=3)).isoformat()},
            {'score': 11, 'timestamp': (now - timedelta(days=2)).isoformat()},
            {'score': 14, 'timestamp': (now - timedelta(days=1)).isoformat()},
            {'score': 12, 'timestamp': now.isoformat()},
        ],
        'average_risk': 11.8,
        'trend': 'stable',
        'category_frequency': {'SAFE': 15, 'THREAT': 1},
        'last_updated': now
    })

    # CHAT003 (Charlie - HIGH RISK - Escalation / Grooming / Secrecy)
    db.risk_scores.insert_one({
        'risk_id': generate_uuid(),
        'conversation_id': 'CHAT003',
        'message_id': 'MSG00031',
        'risk_score': 78,
        'severity': 'HIGH',
        'categories': {
            'GROOMING': 0.78,
            'PRIVACY_RISK': 0.65,
            'MANIPULATION': 0.45,
            'CYBERBULLYING': 0.12,
            'THREAT': 0.08,
            'SELF_HARM': 0.04
        },
        'rule_score': 72,
        'ml_score': 76,
        'context_score': 88,
        'behaviour_score': 74,
        'llm_score': 0,
        'timestamp': now - timedelta(minutes=55),
        'reasons': [
            'Repeated secrecy-related language ("Don\'t tell your parents", "keep it our secret")',
            'Personal information probing and private photo request',
            'Isolation and manipulation pattern detected ("They wouldn\'t understand")',
            'Escalating suspicious behaviour progression over multiple messages',
            'Conversation risk consistently increasing over time'
        ]
    })
    db.behaviour_profiles.insert_one({
        'conversation_id': 'CHAT003',
        'child_id': child_id,
        'contact_id': charlie_id,
        'risk_history': [
            {'score': 10, 'timestamp': (now - timedelta(days=4)).isoformat()},
            {'score': 15, 'timestamp': (now - timedelta(days=3)).isoformat()},
            {'score': 28, 'timestamp': (now - timedelta(days=2)).isoformat()},
            {'score': 52, 'timestamp': (now - timedelta(days=1)).isoformat()},
            {'score': 78, 'timestamp': now.isoformat()},
        ],
        'average_risk': 36.6,
        'trend': 'increasing',
        'category_frequency': {'GROOMING': 8, 'PRIVACY_RISK': 5, 'MANIPULATION': 4},
        'last_updated': now
    })

    # Create Alert for CHAT003
    alert_id = generate_uuid()
    db.alerts.insert_one({
        'alert_id': alert_id,
        'child_id': child_id,
        'conversation_id': 'CHAT003',
        'contact_id': charlie_id,
        'contact_name': 'Charlie',
        'severity': 'HIGH',
        'risk_score': 78,
        'categories': ['GROOMING', 'PRIVACY_RISK', 'MANIPULATION'],
        'reasons': [
            'Repeated secrecy-related language ("Don\'t tell your parents", "keep it our secret")',
            'Private photo request targeting child',
            'Escalating behaviour pattern across 15 messages'
        ],
        'created_at': now - timedelta(minutes=50),
        'status': 'NEW',
        'acknowledged_at': None
    })

    # CHAT004 (David - SAFE - Sports Discussion)
    db.risk_scores.insert_one({
        'risk_id': generate_uuid(),
        'conversation_id': 'CHAT004',
        'message_id': 'MSG00039',
        'risk_score': 10,
        'severity': 'SAFE',
        'categories': {'SAFE': 0.90, 'THREAT': 0.06},
        'rule_score': 5,
        'ml_score': 12,
        'context_score': 8,
        'behaviour_score': 6,
        'llm_score': 0,
        'timestamp': now - timedelta(minutes=80),
        'reasons': [
            'Sports and recreation discussion context verified',
            'Hyperbolic competitive slang ("killed them in cricket") recognized as non-threatening',
            'Mutual friendly coordination for weekend match'
        ]
    })
    db.behaviour_profiles.insert_one({
        'conversation_id': 'CHAT004',
        'child_id': child_id,
        'contact_id': david_id,
        'risk_history': [
            {'score': 8, 'timestamp': (now - timedelta(days=4)).isoformat()},
            {'score': 9, 'timestamp': (now - timedelta(days=3)).isoformat()},
            {'score': 7, 'timestamp': (now - timedelta(days=2)).isoformat()},
            {'score': 11, 'timestamp': (now - timedelta(days=1)).isoformat()},
            {'score': 10, 'timestamp': now.isoformat()},
        ],
        'average_risk': 9.0,
        'trend': 'stable',
        'category_frequency': {'SAFE': 10},
        'last_updated': now
    })
    print('Created risk scores, behavioural trend profiles, and initial safety alerts.')
    
    print('\n' + '='*50)
    print('DEMO ACCOUNTS')
    print('='*50)
    print(f'{"Role":<12} {"Email":<25} {"Password"}')
    print('-'*50)
    print(f'{"Parent":<12} {"parent@example.com":<25} demo123')
    print(f'{"Child":<12} {"child@example.com":<25} demo123')
    print(f'{"Contact":<12} {"alice@example.com":<25} demo123')
    print(f'{"Contact":<12} {"bob@example.com":<25} demo123')
    print(f'{"Contact":<12} {"charlie@example.com":<25} demo123')
    print(f'{"Contact":<12} {"david@example.com":<25} demo123')
    print('='*50)
    print('\nSeed data created successfully!')

if __name__ == '__main__':
    seed()
