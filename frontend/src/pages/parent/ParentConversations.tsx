import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../../services/api';
import { Conversation } from '../../types';
import { GlassCard } from '../../components/common/GlassCard';
import { StatusBadge } from '../../components/common/StatusBadge';
import { RiskBar } from '../../components/common/RiskBar';
import { LoadingSpinner, EmptyState } from '../../components/common/States';
import { MessageSquare, ArrowRight, ShieldCheck } from 'lucide-react';

export const ParentConversations: React.FC = () => {
  const navigate = useNavigate();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchConvs = async () => {
      try {
        setLoading(true);
        const res = await api.get('/parent/conversations');
        setConversations(res.data.conversations || []);
      } catch (err) {
        console.error('Failed to load child conversations', err);
      } finally {
        setLoading(false);
      }
    };
    fetchConvs();
  }, []);

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between pb-4 border-b border-white/10">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <MessageSquare className="w-5 h-5 text-cyan-400" />
            <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
              Monitored Child Conversations
            </h1>
          </div>
          <p className="text-xs text-slate-400">
            Privacy-first overview of active channels with contextual safety indicators.
          </p>
        </div>
        <span className="text-xs font-mono text-slate-500">
          {conversations.length} Tracked Contacts
        </span>
      </div>

      {loading ? (
        <LoadingSpinner size="lg" text="Loading conversation telemetry..." />
      ) : conversations.length === 0 ? (
        <EmptyState title="No Conversations Monitored" description="No channels found for your child." />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {conversations.map((conv) => (
            <GlassCard
              key={conv.conversation_id}
              hover
              glow={conv.severity === 'HIGH' || conv.severity === 'CRITICAL' ? 'red' : 'blue'}
              onClick={() => navigate(`/parent/risk/${conv.conversation_id}`)}
              className="cursor-pointer p-5 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between gap-3 mb-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-slate-800 border border-white/10 flex items-center justify-center font-bold text-sm text-cyan-300">
                      {conv.contact_name?.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <h3 className="font-semibold text-slate-100 text-sm">{conv.contact_name}</h3>
                      <p className="text-[11px] text-slate-500 font-mono">
                        Channel ID: {conv.conversation_id}
                      </p>
                    </div>
                  </div>
                  <StatusBadge severity={conv.severity || 'SAFE'} size="sm" />
                </div>

                <div className="my-4">
                  <RiskBar score={conv.risk_score || 0} label="Current Safety Risk Index" size="md" />
                </div>
              </div>

              <div className="pt-3 border-t border-white/5 flex items-center justify-between text-[11px] text-slate-400 font-mono">
                <span>{conv.message_count || 0} messages analyzed</span>
                <span className="text-cyan-400 font-sans font-medium flex items-center gap-1">
                  <span>Detailed Analysis</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </span>
              </div>
            </GlassCard>
          ))}
        </div>
      )}
    </div>
  );
};
