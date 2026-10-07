import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useSocket } from '../../context/SocketContext';
import { Conversation } from '../../types';
import { api } from '../../services/api';
import { GlassCard } from '../../components/common/GlassCard';
import { LoadingSpinner, EmptyState } from '../../components/common/States';
import { MessageSquare, Circle, ArrowRight, ShieldCheck } from 'lucide-react';

export const ContactDashboard: React.FC = () => {
  const { user } = useAuth();
  const { isUserOnline, subscribe } = useSocket();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const fetchConversations = React.useCallback(async () => {
    try {
      const res = await api.get('/conversations');
      setConversations(res.data.conversations || []);
    } catch (err) {
      console.error('Failed to load contact conversation', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    setLoading(true);
    fetchConversations();
  }, [fetchConversations]);

  useEffect(() => {
    return subscribe((event) => {
      if (event.type === 'message' || event.type === 'unread_count' || event.type === 'status' || event.type === 'connected') {
        fetchConversations();
      }
    });
  }, [subscribe, fetchConversations]);

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Contact Welcome */}
      <div className="p-6 glass-card border-white/10 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-mono text-emerald-400 font-semibold uppercase tracking-wider">
              Connected Contact Workspace
            </span>
          </div>
          <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
            Welcome, {user?.name || 'Contact'}
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Secure client environment for messaging with your connected peer.
          </p>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-mono">
          <ShieldCheck className="w-4 h-4" />
          <span>Active Test Session</span>
        </div>
      </div>

      {/* Conversations - Only their own conversation */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold text-slate-200 tracking-wide flex items-center gap-2">
            <MessageSquare className="w-4 h-4 text-emerald-400" />
            <span>My Active Conversations</span>
          </h2>
          <span className="text-xs text-slate-500 font-mono">
            {conversations.length} Active Channel
          </span>
        </div>

        {loading ? (
          <LoadingSpinner size="lg" text="Loading communication channel..." />
        ) : conversations.length === 0 ? (
          <EmptyState
            title="No Active Channels"
            description="You are not currently linked to any active child conversation channel."
          />
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {conversations.map((conv) => {
              const isOnline = isUserOnline(conv.contact_id);

              return (
                <GlassCard
                  key={conv.conversation_id}
                  hover
                  glow="green"
                  onClick={() => navigate(`/contact/chat/${conv.conversation_id}`)}
                  className="cursor-pointer p-5 border-white/10"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div className="flex items-center gap-3">
                      <div className="relative">
                        <div className="w-12 h-12 rounded-full bg-gradient-to-tr from-emerald-600 to-teal-500 flex items-center justify-center font-bold text-white text-base shadow-md">
                          {conv.contact_name?.charAt(0).toUpperCase() || 'C'}
                        </div>
                        <span
                          className={`absolute bottom-0 right-0 w-3 h-3 rounded-full border-2 border-[#0a0a0f] ${
                            isOnline ? 'bg-emerald-400' : 'bg-slate-500'
                          }`}
                        />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="font-semibold text-slate-100 text-sm">
                            {conv.contact_name} (Child)
                          </h3>
                          {conv.unread_count && conv.unread_count > 0 ? (
                            <span className="px-2 py-0.5 rounded-full bg-cyan-500 text-slate-950 font-bold text-xs font-mono">
                              {conv.unread_count} new
                            </span>
                          ) : null}
                        </div>
                        <p className="text-xs text-slate-400 mt-1 max-w-md truncate">
                          {conv.last_message || 'Start messaging...'}
                        </p>
                        <div className="flex items-center gap-3 text-[11px] text-slate-500 mt-1.5 font-mono">
                          <span className="flex items-center gap-1">
                            <Circle
                              className={`w-1.5 h-1.5 ${
                                isOnline ? 'fill-emerald-400 text-emerald-400' : 'fill-slate-500 text-slate-500'
                              }`}
                            />
                            <span>{isOnline ? 'Online' : 'Offline'}</span>
                          </span>
                          <span>•</span>
                          <span>Channel: {conv.conversation_id}</span>
                        </div>
                      </div>
                    </div>

                    <div className="self-end sm:self-center">
                      <span className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold text-xs shadow-md transition-colors">
                        <span>Open Channel</span>
                        <ArrowRight className="w-4 h-4" />
                      </span>
                    </div>
                  </div>
                </GlassCard>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
