import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../../services/api';
import { Alert, SeverityLevel, AlertStatus } from '../../types';
import { GlassCard } from '../../components/common/GlassCard';
import { StatusBadge } from '../../components/common/StatusBadge';
import { LoadingSpinner, EmptyState } from '../../components/common/States';
import { AlertTriangle, CheckCircle, Check, Eye, Filter } from 'lucide-react';

export const ParentAlerts: React.FC = () => {
  const navigate = useNavigate();
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'critical' | 'high' | 'moderate' | 'resolved'>('all');

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const res = await api.get('/parent/alerts');
      setAlerts(res.data.alerts || []);
    } catch (err) {
      console.error('Failed to load alerts', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, []);

  const handleAcknowledge = async (alertId: string) => {
    try {
      await api.patch(`/parent/alerts/${alertId}/acknowledge`);
      fetchAlerts();
    } catch (err) {
      console.error('Failed to acknowledge alert', err);
    }
  };

  const handleResolve = async (alertId: string) => {
    try {
      await api.patch(`/parent/alerts/${alertId}/resolve`);
      fetchAlerts();
    } catch (err) {
      console.error('Failed to resolve alert', err);
    }
  };

  const filteredAlerts = alerts.filter((alert) => {
    if (filter === 'all') return true;
    if (filter === 'critical') return alert.severity === 'CRITICAL';
    if (filter === 'high') return alert.severity === 'HIGH';
    if (filter === 'moderate') return alert.severity === 'MODERATE';
    if (filter === 'resolved') return alert.status === 'RESOLVED';
    return true;
  });

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-white/10">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <AlertTriangle className="w-5 h-5 text-orange-400" />
            <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
              Security Alert Center
            </h1>
          </div>
          <p className="text-xs text-slate-400">
            Explainable notifications triggered when conversations reach meaningful risk thresholds.
          </p>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-1.5 bg-black/40 p-1 rounded-xl border border-white/10 text-xs font-mono">
          {(['all', 'critical', 'high', 'moderate', 'resolved'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setFilter(tab)}
              className={`px-3 py-1.5 rounded-lg capitalize transition-all cursor-pointer ${
                filter === tab
                  ? 'bg-cyan-500 text-slate-950 font-bold shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <LoadingSpinner size="lg" text="Loading security telemetry alerts..." />
      ) : filteredAlerts.length === 0 ? (
        <EmptyState
          icon={<CheckCircle className="w-6 h-6 text-emerald-400" />}
          title="No Alerts Detected"
          description="Your child's conversations do not currently present any safety concerns that exceed threshold criteria."
        />
      ) : (
        <div className="space-y-4">
          {filteredAlerts.map((alert) => {
            const isResolved = alert.status === 'RESOLVED';
            const isAck = alert.status === 'ACKNOWLEDGED';

            return (
              <GlassCard
                key={alert.alert_id}
                glow={alert.severity === 'CRITICAL' ? 'red' : alert.severity === 'HIGH' ? 'red' : 'blue'}
                className="p-5 border-white/10"
              >
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                  <div className="space-y-2">
                    <div className="flex items-center gap-3">
                      <StatusBadge severity={alert.severity} size="md" />
                      <span className="font-mono text-xs text-slate-400">
                        Risk Score: <strong className="text-white">{alert.risk_score}%</strong>
                      </span>
                      <span className="text-slate-600">•</span>
                      <span className="text-[11px] font-mono text-slate-500">
                        {new Date(alert.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                      {isResolved && (
                        <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          RESOLVED
                        </span>
                      )}
                      {isAck && !isResolved && (
                        <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-blue-500/10 text-cyan-400 border border-cyan-500/20">
                          ACKNOWLEDGED
                        </span>
                      )}
                    </div>

                    <h3 className="text-base font-semibold text-white">
                      Conversation with {alert.contact_name}
                    </h3>

                    {alert.reasons && alert.reasons.length > 0 && (
                      <p className="text-xs text-slate-300 max-w-2xl leading-relaxed">
                        {alert.reasons[0]}
                      </p>
                    )}

                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {alert.categories?.map((cat) => (
                        <span
                          key={cat}
                          className="px-2.5 py-0.5 rounded text-[11px] font-mono bg-white/5 border border-white/10 text-cyan-300"
                        >
                          {cat}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="flex flex-wrap sm:flex-col gap-2 shrink-0 self-end sm:self-center">
                    <button
                      onClick={() => navigate(`/parent/risk/${alert.conversation_id}`)}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold text-xs shadow-md transition-colors cursor-pointer"
                    >
                      <Eye className="w-3.5 h-3.5" />
                      <span>View Analysis</span>
                    </button>

                    {alert.status === 'NEW' && (
                      <button
                        onClick={() => handleAcknowledge(alert.alert_id)}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-slate-300 border border-white/10 text-xs font-medium transition-colors cursor-pointer"
                      >
                        <Check className="w-3.5 h-3.5" />
                        <span>Acknowledge</span>
                      </button>
                    )}

                    {alert.status !== 'RESOLVED' && (
                      <button
                        onClick={() => handleResolve(alert.alert_id)}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-xs font-medium transition-colors cursor-pointer"
                      >
                        <CheckCircle className="w-3.5 h-3.5" />
                        <span>Resolve</span>
                      </button>
                    )}
                  </div>
                </div>
              </GlassCard>
            );
          })}
        </div>
      )}
    </div>
  );
};
