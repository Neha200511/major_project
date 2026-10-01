export type UserRole = 'CHILD' | 'PARENT' | 'CONTACT';
export type SeverityLevel = 'SAFE' | 'MODERATE' | 'HIGH' | 'CRITICAL';
export type AlertStatus = 'NEW' | 'VIEWED' | 'ACKNOWLEDGED' | 'RESOLVED';

export interface User {
  _id: string;
  name: string;
  email: string;
  role: UserRole;
  avatar?: string | null;
  created_at?: string;
  last_active?: string;
  status: 'online' | 'offline';
}

export interface Message {
  message_id: string;
  conversation_id: string;
  sender_id: string;
  receiver_id: string;
  content: string;
  timestamp: string;
  message_type?: string;
  delivery_status: 'sent' | 'delivered' | 'read';
}

export interface Conversation {
  conversation_id: string;
  participants: string[];
  created_at: string;
  updated_at: string;
  last_message_at: string;
  status?: string;
  contact_name?: string;
  contact_id?: string;
  contact_status?: 'online' | 'offline';
  contact_last_active?: string;
  last_message?: string;
  unread_count?: number;
  risk_score?: number;
  severity?: SeverityLevel;
  message_count?: number;
}

export interface Alert {
  alert_id: string;
  child_id: string;
  conversation_id: string;
  contact_id: string;
  contact_name: string;
  severity: SeverityLevel;
  risk_score: number;
  categories: string[];
  reasons: string[];
  created_at: string;
  status: AlertStatus;
  acknowledged_at?: string | null;
}

export interface RiskData {
  risk_score: number;
  severity: SeverityLevel;
  categories: Record<string, number>;
  layer_scores: {
    rule: number;
    ml: number;
    context: number;
    behaviour: number;
    llm: number;
  };
  reasons: string[];
}

export interface TrendData {
  risk_history: Array<{ score: number; timestamp: string }>;
  trend: 'increasing' | 'decreasing' | 'stable' | 'new';
  average_risk: number;
  category_frequency: Record<string, number>;
}

export interface ParentOverview {
  safety_status: 'SAFE' | 'ATTENTION' | 'HIGH RISK';
  active_conversations: number;
  open_alerts: number;
  high_risk_contacts: number;
  overall_risk_score: number;
}

export interface ReportSummary {
  total_messages: number;
  total_alerts: number;
  conversations: Array<{
    conversation_id: string;
    contact_name: string;
    message_count: number;
    risk_score: number;
    severity: SeverityLevel;
  }>;
  category_distribution: Record<string, number>;
  generated_at: string;
}

export interface DevStatus {
  connected_users: number;
  online_users: string[];
  total_messages: number;
  total_conversations: number;
  total_alerts: number;
  total_users: number;
  ml_model: {
    loaded: boolean;
    metrics: Record<string, any>;
  };
  database_status: string;
  environment: string;
}
