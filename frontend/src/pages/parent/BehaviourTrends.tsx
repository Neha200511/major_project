import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { Conversation, TrendData } from '../../types';
import { GlassCard } from '../../components/common/GlassCard';
import { LoadingSpinner } from '../../components/common/States';
import { TrendingUp, Activity, BarChart2, CheckCircle2 } from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  BarChart,
  Bar,
} from 'recharts';

export const BehaviourTrends: React.FC = () => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConvId, setSelectedConvId] = useState<string>('CHAT003'); // Default to Charlie (escalation)
  const [trendData, setTrendData] = useState<TrendData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchConvs = async () => {
      try {
        const res = await api.get('/parent/conversations');
        const convs = res.data.conversations || [];
        setConversations(convs);
        if (convs.length > 0 && !selectedConvId) {
          setSelectedConvId(convs[0].conversation_id);
        }
      } catch (err) {
        console.error('Failed to load conversations', err);
      }
    };
    fetchConvs();
  }, []);

  useEffect(() => {
    const fetchTrend = async () => {
      if (!selectedConvId) return;
      try {
        setLoading(true);
        const res = await api.get(`/parent/trends/${selectedConvId}`);
        setTrendData(res.data);
      } catch (err) {
        console.error('Failed to load trend data', err);
      } finally {
        setLoading(false);
      }
    };
    fetchTrend();
  }, [selectedConvId]);

  const selectedConv = conversations.find((c) => c.conversation_id === selectedConvId);

  const chartHistory = (trendData?.risk_history || []).map((h, i) => ({
    label: `Point ${i + 1}`,
    score: h.score,
  }));

  const categoryFrequencyData = Object.entries(trendData?.category_frequency || {}).map(
    ([name, count]) => ({
      category: name.replace('_', ' '),
      occurrences: count,
    })
  );

  const getTrendBadge = (trend?: string) => {
    if (trend === 'increasing') {
      return (
        <span className="px-3 py-1 rounded-full text-xs font-semibold font-mono bg-red-500/15 text-red-400 border border-red-500/30">
          Risk Trend: Increasing ↗
        </span>
      );
    }
    if (trend === 'decreasing') {
      return (
        <span className="px-3 py-1 rounded-full text-xs font-semibold font-mono bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
          Risk Trend: Decreasing ↘
        </span>
      );
    }
    return (
      <span className="px-3 py-1 rounded-full text-xs font-semibold font-mono bg-blue-500/15 text-cyan-300 border border-cyan-500/30">
        Risk Trend: Stable →
      </span>
    );
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header & Conversation Selector */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-white/10">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <TrendingUp className="w-5 h-5 text-cyan-400" />
            <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
              Behavioral Pattern Analysis
            </h1>
          </div>
          <p className="text-xs text-slate-400">
            Gradual escalation detection and sustained category recurrence over time.
          </p>
        </div>

        {/* Conversation Dropdown */}
        <div className="flex items-center gap-2">
          <label className="text-xs text-slate-400 font-medium">Channel:</label>
          <select
            value={selectedConvId}
            onChange={(e) => setSelectedConvId(e.target.value)}
            className="glass-input rounded-xl px-3 py-2 text-xs font-semibold text-white bg-[#0d0d15] border-white/10 focus:ring-1 focus:ring-cyan-500"
          >
            {conversations.map((c) => (
              <option key={c.conversation_id} value={c.conversation_id}>
                {c.contact_name} ({c.conversation_id})
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <LoadingSpinner size="lg" text="Processing behavioral telemetry..." />
      ) : (
        <>
          {/* Trend KPI Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <GlassCard className="p-4 flex items-center justify-between">
              <div>
                <span className="text-[11px] text-slate-400 font-mono">Channel Subject</span>
                <h3 className="text-base font-bold text-white mt-0.5">
                  {selectedConv?.contact_name || 'Contact'}
                </h3>
              </div>
              <Activity className="w-6 h-6 text-cyan-400 opacity-60" />
            </GlassCard>

            <GlassCard className="p-4 flex items-center justify-between">
              <div>
                <span className="text-[11px] text-slate-400 font-mono">Average Risk Baseline</span>
                <h3 className="text-base font-bold font-mono text-cyan-300 mt-0.5">
                  {trendData?.average_risk || 0}%
                </h3>
              </div>
              <BarChart2 className="w-6 h-6 text-cyan-400 opacity-60" />
            </GlassCard>

            <GlassCard className="p-4 flex items-center justify-between">
              <div>
                <span className="text-[11px] text-slate-400 font-mono">Trajectory Evaluation</span>
                <div className="mt-1">{getTrendBadge(trendData?.trend)}</div>
              </div>
            </GlassCard>
          </div>

          {/* Historical Progression Chart */}
          <GlassCard className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-cyan-400" />
                  <span>Longitudinal Risk Progression</span>
                </h2>
                <p className="text-xs text-slate-400">
                  Monitors gradual escalation across sequential message exchanges
                </p>
              </div>
              <span className="text-xs font-mono text-slate-500">
                {chartHistory.length} Telemetry Samples
              </span>
            </div>

            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartHistory}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="label" stroke="#64748b" tick={{ fontSize: 11 }} />
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
                    dataKey="score"
                    stroke="#00e5ff"
                    strokeWidth={3}
                    dot={{ r: 5, fill: '#00a8ff', stroke: '#fff', strokeWidth: 2 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </GlassCard>

          {/* Category Frequency Chart */}
          {categoryFrequencyData.length > 0 && (
            <GlassCard className="p-6">
              <h2 className="text-sm font-semibold text-slate-100 mb-4 flex items-center gap-2">
                <BarChart2 className="w-4 h-4 text-cyan-400" />
                <span>Recurrent Indicator Frequency</span>
              </h2>

              <div className="h-56 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={categoryFrequencyData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                    <XAxis dataKey="category" stroke="#64748b" tick={{ fontSize: 11 }} />
                    <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#12121a',
                        borderColor: 'rgba(255,255,255,0.1)',
                        borderRadius: '0.5rem',
                        fontSize: '12px',
                        color: '#f8fafc',
                      }}
                    />
                    <Bar dataKey="occurrences" fill="#7c3aed" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </GlassCard>
          )}
        </>
      )}
    </div>
  );
};
