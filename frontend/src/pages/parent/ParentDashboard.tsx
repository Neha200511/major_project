import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../../services/api';
import { ParentOverview, Conversation, Alert } from '../../types';
import { GlassCard } from '../../components/common/GlassCard';
import { StatusBadge } from '../../components/common/StatusBadge';
import { RiskBar } from '../../components/common/RiskBar';
import { LoadingSpinner } from '../../components/common/States';
import {
  Shield,
  ShieldCheck,
  AlertTriangle,
  MessageSquare,
  Users,
  Activity,
  ArrowRight,
  TrendingUp,
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts';

export const ParentDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [overview, setOverview] = useState<ParentOverview | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [recentAlerts, setRecentAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState<'24h' | '7d' | '30d'>('7d');

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        const [overviewRes, convsRes, alertsRes] = await Promise.all([
          api.get('/parent/overview'),
          api.get('/parent/conversations'),
          api.get('/parent/alerts?limit=5'),
        ]);
        setOverview(overviewRes.data);
        setConversations(convsRes.data.conversations || []);
        setRecentAlerts(alertsRes.data.alerts || []);
      } catch (err) {
        console.error('Failed to load parent dashboard', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  // Aggregated trend data for overall graph
  const trendData = [
    { time: 'Mon', risk: 10 },
    { time: 'Tue', risk: 12 },
    { time: 'Wed', risk: 22 },
    { time: 'Thu', risk: 38 },
    { time: 'Fri', risk: 27 },
    { time: 'Sat', risk: 25 },
    { time: 'Sun', risk: Math.round(overview?.overall_risk_score || 27) },
  ];

  if (loading) {
    return <LoadingSpinner size="lg" text="Loading security operations center..." />;
  }

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header Banner (Requirement #51) */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 glass-card border-cyan-500/20 shadow-[0_0_25px_rgba(0,168,255,0.1)]">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="text-xs font-mono text-cyan-400 font-semibold tracking-wider uppercase">
              Parent Security Operations Center
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
            Child Safety Overview
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 mt-1">
            Privacy-first conversational risk monitoring & behavioral pattern telemetry.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="text-right">
            <div className="text-[11px] font-mono text-slate-400">Current Safety Assessment</div>
            <div className="mt-1">
              <StatusBadge severity={overview?.safety_status || 'SAFE'} size="lg" />
            </div>
          </div>
        </div>
      </div>

      {/* Top 4 KPI Metrics Grid (Requirement #30) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* KPI 1 */}
        <GlassCard hover glow="blue" className="p-5">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-medium text-slate-400">Active Conversations</span>
            <div className="p-2 rounded-lg bg-blue-500/10 text-cyan-400">
              <MessageSquare className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold font-mono text-white">
            {overview?.active_conversations || 0}
          </div>
          <p className="text-[11px] text-slate-500 mt-1 font-mono">Isolated peer channels</p>
        </GlassCard>

        {/* KPI 2 */}
        <GlassCard hover glow="red" className="p-5">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-medium text-slate-400">Open Risk Alerts</span>
            <div className="p-2 rounded-lg bg-red-500/10 text-red-400">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold font-mono text-red-400">
            {overview?.open_alerts || 0}
          </div>
          <p className="text-[11px] text-slate-500 mt-1 font-mono">Requires parent attention</p>
        </GlassCard>

        {/* KPI 3 */}
        <GlassCard hover glow="purple" className="p-5">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-medium text-slate-400">Flagged Contacts</span>
            <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400">
              <Users className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold font-mono text-purple-300">
            {overview?.high_risk_contacts || 0}
          </div>
          <p className="text-[11px] text-slate-500 mt-1 font-mono">Risk score &ge; 60%</p>
        </GlassCard>

        {/* KPI 4 */}
        <GlassCard hover glow="green" className="p-5">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-medium text-slate-400">Aggregate Risk Index</span>
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
              <Activity className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold font-mono text-emerald-400">
            {overview?.overall_risk_score || 0}%
          </div>
          <p className="text-[11px] text-slate-500 mt-1 font-mono">0-29% Safe baseline</p>
        </GlassCard>
      </div>

      {/* Charts & Contact Risk Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Trend Graph (2 Columns) */}
        <GlassCard className="lg:col-span-2 p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-cyan-400" />
                <span>Conversational Risk Trend</span>
              </h2>
              <p className="text-xs text-slate-400">Multi-day fused risk telemetry trajectory</p>
            </div>
            <div className="flex items-center gap-1 bg-black/40 p-1 rounded-lg border border-white/5 text-xs font-mono">
              {(['24h', '7d', '30d'] as const).map((r) => (
                <button
                  key={r}
                  onClick={() => setTimeRange(r)}
                  className={`px-2.5 py-1 rounded-md transition-all cursor-pointer ${
                    timeRange === r
                      ? 'bg-cyan-500 text-slate-950 font-bold shadow-sm'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  {r}
                </button>
              ))}
            </div>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="time" stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis domain={[0, 100]} stroke="#64748b" tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#12121a',
                    borderColor: 'rgba(255,255,255,0.1)',
                    borderRadius: '0.5rem',
                    fontSize: '12px',
                    color: '#f8fafc',
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="risk"
                  stroke="#00e5ff"
                  strokeWidth={2.5}
                  dot={{ r: 4, fill: '#00a8ff', stroke: '#fff', strokeWidth: 1.5 }}
                  activeDot={{ r: 6, fill: '#00e5ff' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="mt-4 pt-3 border-t border-white/5 flex items-center justify-between text-[11px] text-slate-400 font-mono">
            <span>Thresholds: Safe &lt; 30% | Moderate 30-59% | High 60-79% | Critical &gt; 80%</span>
            <span className="text-cyan-400">Autonomous Fusion Active</span>
          </div>
        </GlassCard>

        {/* Contact-Wise Risk Overview (1 Column) (Requirement #31) */}
        <GlassCard className="p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
                <Users className="w-4 h-4 text-cyan-400" />
                <span>Contact-Wise Risk</span>
              </h2>
              <span className="text-[11px] font-mono text-slate-500">Live Telemetry</span>
            </div>

            <div className="space-y-4">
              {conversations.map((conv) => (
                <div
                  key={conv.conversation_id}
                  onClick={() => navigate(`/parent/risk/${conv.conversation_id}`)}
                  className="p-3 rounded-xl bg-white/[0.02] hover:bg-white/[0.05] border border-white/5 transition-all cursor-pointer group"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-semibold text-xs text-slate-200 group-hover:text-cyan-300 transition-colors">
                      {conv.contact_name}
                    </span>
                    <StatusBadge severity={conv.severity || 'SAFE'} size="sm" />
                  </div>
                  <RiskBar score={conv.risk_score || 0} size="sm" />
                </div>
              ))}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-white/5 text-center">
            <button
              onClick={() => navigate('/parent/conversations')}
              className="text-xs text-cyan-400 hover:text-cyan-300 font-medium inline-flex items-center gap-1 cursor-pointer"
            >
              <span>View detailed conversation telemetry</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </GlassCard>
      </div>

      {/* Recent Alerts Table (Requirement #35) */}
      <GlassCard className="p-5">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-orange-400" />
            <h2 className="text-sm font-semibold text-slate-100">Recent Security Alerts</h2>
          </div>
          <button
            onClick={() => navigate('/parent/alerts')}
            className="text-xs text-cyan-400 hover:text-cyan-300 font-medium inline-flex items-center gap-1 cursor-pointer"
          >
            <span>Alert Center ({recentAlerts.length})</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {recentAlerts.length === 0 ? (
          <div className="text-center py-8 text-xs text-slate-500">
            No active alerts detected. All child conversations appear safe.
          </div>
        ) : (
          <div className="space-y-3">
            {recentAlerts.map((alert) => (
              <div
                key={alert.alert_id}
                className="p-4 rounded-xl bg-slate-900/60 border border-white/10 hover:border-cyan-500/30 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3"
              >
                <div className="flex items-start gap-3">
                  <div className="mt-0.5">
                    <StatusBadge severity={alert.severity} size="sm" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-xs sm:text-sm text-slate-100">
                      Concerning Pattern with {alert.contact_name}
                    </h3>
                    <p className="text-xs text-slate-400 mt-0.5">
                      {alert.reasons?.[0] || 'Multiple suspicious conversational indicators detected.'}
                    </p>
                    <div className="flex flex-wrap gap-1.5 mt-2">
                      {alert.categories?.map((cat) => (
                        <span
                          key={cat}
                          className="px-2 py-0.5 rounded text-[10px] font-mono bg-white/5 border border-white/10 text-cyan-300"
                        >
                          {cat}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 self-end sm:self-center shrink-0">
                  <button
                    onClick={() => navigate(`/parent/risk/${alert.conversation_id}`)}
                    className="px-3 py-1.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold text-xs transition-colors cursor-pointer"
                  >
                    View Analysis
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </GlassCard>
    </div>
  );
};
