import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { api } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import { useSocket } from '../../context/SocketContext';
import type { Conversation } from '../../types';
import { ChatWindow } from './ChatWindow';
import { LoadingSpinner } from '../common/States';
import { MessageSquare, Search, Lock } from 'lucide-react';

interface MessengerProps {
  /** e.g. '/child/chat' or '/contact/chat' */
  basePath: string;
}

const shortTime = (ts?: string) => {
  if (!ts) return '';
  const iso = !/[zZ]|[+-]\d\d:?\d\d$/.test(ts) ? `${ts}Z` : ts;
  const d = new Date(iso);
  if (isNaN(d.getTime())) return '';
  const today = new Date();
  return d.toDateString() === today.toDateString()
    ? d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    : d.toLocaleDateString([], { day: 'numeric', month: 'short' });
};

/**
 * WhatsApp-style messenger: conversation list on the left, active chat in the centre.
 * Everything updates live over the WebSocket.
 */
export const Messenger: React.FC<MessengerProps> = ({ basePath }) => {
  const { conversationId } = useParams<{ conversationId?: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { subscribe, isUserOnline, typingMap, unreadMap } = useSocket();

  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState('');

  const load = useCallback(async () => {
    try {
      const res = await api.get('/conversations');
      setConversations(res.data.conversations || []);
    } catch (err) {
      console.error('Failed to load conversations', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  // Live: update preview + move conversation to the top on every new message
  useEffect(() => {
    return subscribe((event) => {
      if (event.type === 'message') {
        const m = event.message;
        setConversations((prev) => {
          const idx = prev.findIndex((c) => c.conversation_id === m.conversation_id);
          if (idx === -1) {
            load();
            return prev;
          }
          const updated = { ...prev[idx], last_message: m.content, last_message_at: m.timestamp };
          return [updated, ...prev.filter((_, i) => i !== idx)];
        });
      } else if (event.type === 'connected') {
        load();
      }
    });
  }, [subscribe, load]);

  // If there's only 1 conversation (typical for contacts), auto-navigate to it
  useEffect(() => {
    if (!conversationId && conversations.length === 1) {
      navigate(`${basePath}/${conversations[0].conversation_id}`, { replace: true });
    }
  }, [conversationId, conversations, basePath, navigate]);

  const active = conversations.find((c) => c.conversation_id === conversationId);

  const filtered = conversations.filter((c) =>
    (c.contact_name || '').toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="h-[calc(100vh-7.5rem)] md:h-[calc(100vh-6.5rem)] -m-4 sm:-m-6 lg:-m-8 flex border-t border-white/5 bg-[#0b0b12]">
      {/* Conversation list */}
      <aside
        className={`${conversationId ? 'hidden md:flex' : 'flex'} w-full md:w-80 lg:w-96 flex-col border-r border-white/10 bg-[#0d0d15]`}
      >
        <div className="px-4 pt-4 pb-3 border-b border-white/10">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-base font-semibold text-white">Chats</h2>
            <span className="text-[11px] text-slate-500 font-mono">{user?.name}</span>
          </div>
          <div className="relative">
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search chats"
              className="w-full glass-input rounded-lg pl-9 pr-3 py-2 text-xs text-slate-100 placeholder:text-slate-500"
            />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <LoadingSpinner size="md" text="Loading chats..." />
          ) : filtered.length === 0 ? (
            <p className="text-xs text-slate-500 text-center p-6">No conversations found.</p>
          ) : (
            filtered.map((c) => {
              const online = isUserOnline(c.contact_id);
              const typing = !!typingMap[c.conversation_id];
              const unread =
                c.conversation_id === conversationId
                  ? 0
                  : unreadMap[c.conversation_id] ?? c.unread_count ?? 0;
              const selected = c.conversation_id === conversationId;
              return (
                <button
                  key={c.conversation_id}
                  onClick={() => navigate(`${basePath}/${c.conversation_id}`)}
                  className={`w-full flex items-center gap-3 px-4 py-3 text-left border-b border-white/5 transition-colors cursor-pointer ${
                    selected ? 'bg-cyan-500/10 border-l-2 border-l-cyan-400' : 'hover:bg-white/[0.04]'
                  }`}
                >
                  <div className="relative shrink-0">
                    <div className="w-11 h-11 rounded-full bg-gradient-to-tr from-cyan-600 to-blue-500 flex items-center justify-center font-bold text-white">
                      {(c.contact_name || '?').charAt(0).toUpperCase()}
                    </div>
                    <span
                      className={`absolute bottom-0 right-0 w-3 h-3 rounded-full border-2 border-[#0d0d15] ${
                        online ? 'bg-emerald-400' : 'bg-slate-500'
                      }`}
                      title={online ? 'Online' : 'Offline'}
                    />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-medium text-sm text-slate-100 truncate">{c.contact_name}</span>
                      <span className={`text-[10px] shrink-0 ${unread > 0 ? 'text-cyan-400' : 'text-slate-500'}`}>
                        {shortTime(c.last_message_at)}
                      </span>
                    </div>
                    <div className="flex items-center justify-between gap-2 mt-0.5">
                      <span className={`text-xs truncate ${typing ? 'text-cyan-300 italic' : 'text-slate-400'}`}>
                        {typing ? 'typing…' : c.last_message || (online ? 'Online' : 'Tap to start chatting')}
                      </span>
                      {unread > 0 && (
                        <span className="min-w-5 h-5 px-1.5 rounded-full bg-cyan-500 text-slate-950 text-[10px] font-bold flex items-center justify-center shrink-0">
                          {unread}
                        </span>
                      )}
                    </div>
                  </div>
                </button>
              );
            })
          )}
        </div>
      </aside>

      {/* Active chat */}
      <section className={`${conversationId ? 'flex' : 'hidden md:flex'} flex-1 flex-col min-w-0`}>
        {conversationId && active ? (
          <ChatWindow
            key={active.conversation_id}
            conversationId={active.conversation_id}
            contactName={active.contact_name || 'Contact'}
            contactId={active.contact_id}
            onBack={() => navigate(basePath)}
          />
        ) : conversationId && loading ? (
          <div className="flex-1 flex items-center justify-center">
            <LoadingSpinner size="md" text="Opening chat..." />
          </div>
        ) : conversationId && !active ? (
          <div className="flex-1 flex items-center justify-center text-xs text-slate-400">
            Conversation not found or access denied.
          </div>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-center p-8 cyber-bg">
            <div className="w-16 h-16 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 mb-4">
              <MessageSquare className="w-8 h-8" />
            </div>
            <h3 className="text-lg font-semibold text-white mb-1">Select a chat</h3>
            <p className="text-xs text-slate-400 max-w-xs">
              Choose a conversation from the list to start messaging.
            </p>
            <p className="mt-6 text-[11px] text-slate-500 flex items-center gap-1.5">
              <Lock className="w-3 h-3" /> Secure connection
            </p>
          </div>
        )}
      </section>
    </div>
  );
};
