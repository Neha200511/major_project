from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

def generate_id() -> str:
    return uuid.uuid4().hex[:24]

class UserRole(str, Enum):
    CHILD = 'CHILD'
    PARENT = 'PARENT'
    CONTACT = 'CONTACT'

class UserStatus(str, Enum):
    ONLINE = 'online'
    OFFLINE = 'offline'

class AlertStatus(str, Enum):
    NEW = 'NEW'
    VIEWED = 'VIEWED'
    ACKNOWLEDGED = 'ACKNOWLEDGED'
    RESOLVED = 'RESOLVED'

class Severity(str, Enum):
    SAFE = 'SAFE'
    MODERATE = 'MODERATE'
    HIGH = 'HIGH'
    CRITICAL = 'CRITICAL'

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=5)
    password: str = Field(..., min_length=6)
    role: UserRole

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    _id: str
    name: str
    email: str
    role: str
    avatar: Optional[str] = None
    created_at: Optional[str] = None
    last_active: Optional[str] = None
    status: str = 'offline'

class MessageCreate(BaseModel):
    conversation_id: str
    content: str = Field(..., min_length=1, max_length=5000)

class ConversationCreate(BaseModel):
    participant_id: str

class RiskScoreModel(BaseModel):
    risk_id: str = Field(default_factory=generate_id)
    conversation_id: str
    message_id: str
    risk_score: float = 0.0
    severity: str = 'SAFE'
    categories: Dict[str, float] = {}
    rule_score: float = 0.0
    ml_score: float = 0.0
    context_score: float = 0.0
    behaviour_score: float = 0.0
    llm_score: float = 0.0
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    reasons: List[str] = []

class AlertModel(BaseModel):
    alert_id: str = Field(default_factory=generate_id)
    child_id: str
    conversation_id: str
    contact_id: str
    contact_name: str
    severity: str
    risk_score: float
    categories: List[str] = []
    reasons: List[str] = []
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    status: str = 'NEW'
    acknowledged_at: Optional[str] = None

class BehaviourProfile(BaseModel):
    conversation_id: str
    child_id: str
    contact_id: str
    risk_history: List[Dict[str, Any]] = []
    average_risk: float = 0.0
    trend: str = 'stable'
    category_frequency: Dict[str, int] = {}
    last_updated: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
