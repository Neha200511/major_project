import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useSocket } from '../../context/SocketContext';
import { Conversation } from '../../types';
import { api } from '../../services/api';
import { GlassCard } from '../../components/common/GlassCard';
import { LoadingSpinner, EmptyState } from '../../components/common/States';
import { MessageSquare, Circle, ArrowRight, Shield } from 'lucide-react';

export const ChildDashboard: React.FC = () => {
  const { user } = useAuth();
  const { onlineUsers, latestMessage } = useSocket();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const fetchConversations = async () => {
    try {
      setLoading(true);
      const res = await api.get('/conversations');
      setConversations(res.data.conversations || []);
    } catch (err) {
      console.error('Failed to load conversations', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConversations();
  }, []);

  // Update on new socket message
  useEffect(() => {
    if (latestMessage) {
      fetchConversations();
    }
  }, [latestMessage]);

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Welcome Hero */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-6 glass-card border-cyan-500/20 shadow-[0_0_20px_rgba(0,168,255,0.1)]">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="text-xs font-mono text-cyan-400 font-semibold uppercase tracking-wider">
              Protected Environment
            </span>
          </div>
          <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
            Welcome back, {user?.name || 'Child'}
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Connect and communicate safely with your verified friends.
          </p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-mono">
          <Shield className="w-4 h-4" />
          <span>Active Safe Mode</span>
        </div>
      </div>

      {/* Conversations Grid */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold text-slate-200 tracking-wide flex items-center gap-2">
            <MessageSquare className="w-4 h-4 text-cyan-400" />
            <span>My Conversations</span>
          </h2>
          <span className="text-xs text-slate-500 font-mono">
            {conversations.length} Active Contacts
          </span>
        </div>

        {loading ? (
          <LoadingSpinner size="lg" text="Loading conversations..." />
        ) : conversations.length === 0 ? (
          <EmptyState
            title="No Active Conversations"
            description="Your contact connections will appear here once registered."
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {conversations.map((conv) => {
              const isOnline = conv.contact_id
                ? onlineUsers.includes(conv.contact_id)
                : conv.contact_status === 'online';

              return (
                <GlassCard
                  key={conv.conversation_id}
                  hover
                  glow="blue"
                  onClick={() => navigate(`/child/chat/${conv.conversation_id}`)}
                  className="cursor-pointer flex flex-col justify-between p-5 border-white/10"
                >
                  <div className="flex items-start justify-between gap-3 mb-3">
                    <div className="flex items-center gap-3">
                      <div className="relative">
                        <div className="w-11 h-11 rounded-full bg-gradient-to-tr from-cyan-600 to-blue-500 flex items-center justify-center font-bold text-white text-base shadow-md">
                          {conv.contact_name?.charAt(0).toUpperCase() || 'C'}
                        </div>
                        <span
                          className={`absolute bottom-0 right-0 w-3 h-3 rounded-full border-2 border-[#0a0a0f] ${
                            isOnline ? 'bg-emerald-400' : 'bg-slate-500'
                          }`}
                        />
                      </div>
                      <div>
                        <h3 className="font-semibold text-slate-100 text-sm">
                          {conv.contact_name}
                        </h3>
                        <div className="flex items-center gap-1.5 text-[11px] text-slate-400 mt-0.5">
                          <Circle
                            className={`w-2 h-2 ${
                              isOnline
                                ? 'fill-emerald-400 text-emerald-400'
                                : 'fill-slate-500 text-slate-500'
                            }`}
                          />
                          <span>{isOnline ? 'Online' : 'Offline'}</span>
                        </div>
                      </div>
                    </div>

                    {conv.unread_count && conv.unread_count > 0 ? (
                      <span className="px-2 py-0.5 rounded-full bg-cyan-500 text-slate-950 font-bold text-xs font-mono shadow-[0_0_10px_rgba(0,168,255,0.4)]">
                        {conv.unread_count} new
                      </span>
                    ) : null}
                  </div>

                  {/* Last message preview */}
                  <div className="p-2.5 rounded-lg bg-black/30 border border-white/5 mb-3">
                    <p className="text-xs text-slate-300 truncate">
                      {conv.last_message || 'Start chatting now...'}
                    </p>
                  </div>

                  <div className="flex items-center justify-between pt-2 border-t border-white/5 text-[11px] text-slate-500">
                    <span className="font-mono">ID: {conv.conversation_id}</span>
                    <span className="inline-flex items-center gap-1 text-cyan-400 font-medium hover:underline">
                      <span>Open Chat</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </span>
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
