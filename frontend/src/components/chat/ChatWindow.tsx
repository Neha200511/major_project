import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useSocket } from '../../context/SocketContext';
import type { Message } from '../../types';
import { api } from '../../services/api';
import { Send, Lock, Check, CheckCheck, Clock, ArrowLeft, WifiOff } from 'lucide-react';
import { LoadingSpinner } from '../common/States';

interface ChatWindowProps {
  conversationId: string;
  contactName: string;
  contactId?: string;
  onBack?: () => void;
}

type ChatMessage = Message & { pending?: boolean; client_id?: string };

const formatTime = (ts: string) => {
  const d = new Date(ts);
  return isNaN(d.getTime()) ? '' : d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

const formatDay = (ts: string) => {
  const d = new Date(ts);
  if (isNaN(d.getTime())) return '';
  const today = new Date();
  const yesterday = new Date();
  yesterday.setDate(today.getDate() - 1);
  if (d.toDateString() === today.toDateString()) return 'Today';
  if (d.toDateString() === yesterday.toDateString()) return 'Yesterday';
  return d.toLocaleDateString([], { day: 'numeric', month: 'short', year: 'numeric' });
};

/** Backend timestamps are UTC; make sure JS parses them as UTC. */
const normalizeTs = (ts: string) => (ts && !/[zZ]|[+-]\d\d:?\d\d$/.test(ts) ? `${ts}Z` : ts);

const Ticks: React.FC<{ msg: ChatMessage }> = ({ msg }) => {
  if (msg.pending) return <Clock className="w-3 h-3 text-white/60" />;
  if (msg.delivery_status === 'read') return <CheckCheck className="w-3.5 h-3.5 text-sky-300" />;
  if (msg.delivery_status === 'delivered') return <CheckCheck className="w-3.5 h-3.5 text-white/60" />;
  return <Check className="w-3.5 h-3.5 text-white/60" />;
};

export const ChatWindow: React.FC<ChatWindowProps> = ({ conversationId, contactName, contactId, onBack }) => {
  const { user } = useAuth();
  const myId = user?._id;
  const { sendMessage, sendTyping, sendRead, subscribe, typingMap, isUserOnline, connectionState } = useSocket();

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);

  const isOnline = isUserOnline(contactId);
  const isTyping = !!typingMap[conversationId] && typingMap[conversationId] !== myId;

  const loadMessages = useCallback(async () => {
    try {
      setError(null);
      const res = await api.get(`/messages/${conversationId}?limit=200`);
      const loaded: ChatMessage[] = (res.data.messages || []).map((m: Message) => ({
        ...m,
        timestamp: normalizeTs(m.timestamp),
      }));
      setMessages((prev) => {
        // keep any optimistic messages that the server hasn't confirmed yet
        const pending = prev.filter((m) => m.pending);
        return [...loaded, ...pending];
      });
      sendRead(conversationId);
    } catch (err) {
      console.error('Failed to load messages', err);
      setError('Could not load messages.');
    } finally {
      setLoading(false);
    }
  }, [conversationId, sendRead]);

  // Load history when the conversation changes
  useEffect(() => {
    setLoading(true);
    setMessages([]);
    setInputText('');
    loadMessages();
    inputRef.current?.focus();
  }, [conversationId, loadMessages]);

  // Live updates via WebSocket - no refresh needed
  useEffect(() => {
    return subscribe((event) => {
      if (event.type === 'message' && event.message.conversation_id === conversationId) {
        const incoming: ChatMessage = { ...event.message, timestamp: normalizeTs(event.message.timestamp) };
        setMessages((prev) => {
          // Replace my optimistic copy if this is the server echo
          if (event.client_id) {
            const idx = prev.findIndex((m) => m.client_id === event.client_id);
            if (idx !== -1) {
              const copy = [...prev];
              copy[idx] = incoming;
              return copy;
            }
          }
          if (prev.some((m) => m.message_id === incoming.message_id)) return prev;
          return [...prev, incoming];
        });
        // I'm looking at this chat, so a message from the other person is read immediately
        if (incoming.sender_id !== myId && document.visibilityState === 'visible') {
          sendRead(conversationId);
        }
      } else if (event.type === 'read' && event.conversation_id === conversationId && event.user_id !== myId) {
        // The other person read my messages -> blue double ticks
        setMessages((prev) =>
          prev.map((m) => (m.sender_id === myId && !m.pending ? { ...m, delivery_status: 'read' } : m))
        );
      } else if (event.type === 'delivered' && event.conversation_id === conversationId) {
        setMessages((prev) =>
          prev.map((m) =>
            m.sender_id === myId && m.delivery_status === 'sent' ? { ...m, delivery_status: 'delivered' } : m
          )
        );
      } else if (event.type === 'connected') {
        // Re-sync anything missed while disconnected
        loadMessages();
      }
    });
  }, [subscribe, conversationId, myId, sendRead, loadMessages]);

  // Mark as read when the tab becomes visible again
  useEffect(() => {
    const onVisible = () => {
      if (document.visibilityState === 'visible') sendRead(conversationId);
    };
    document.addEventListener('visibilitychange', onVisible);
    return () => document.removeEventListener('visibilitychange', onVisible);
  }, [conversationId, sendRead]);

  // Auto-scroll to newest message
  useEffect(() => {
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages, isTyping]);

  const handleSend = (e?: React.FormEvent) => {
    e?.preventDefault();
    const text = inputText.trim();
    if (!text || !myId) return;

    const clientId = `c_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
    const optimistic: ChatMessage = {
      message_id: clientId,
      client_id: clientId,
      conversation_id: conversationId,
      sender_id: myId,
      receiver_id: contactId || '',
      content: text,
      timestamp: new Date().toISOString(),
      delivery_status: 'sent',
      pending: true,
    };
    setMessages((prev) => [...prev, optimistic]);
    sendMessage(conversationId, text, clientId);
    setInputText('');
    inputRef.current?.focus();
  };

  const statusLine = isTyping ? 'typing…' : isOnline ? 'online' : 'offline';

  return (
    <div className="flex flex-col h-full bg-[#0b0b12] overflow-hidden">
      {/* Header: who you're chatting with */}
      <div className="px-4 py-3 bg-slate-900/90 border-b border-white/10 flex items-center justify-between gap-3">
        <div className="flex items-center gap-3 min-w-0">
          {onBack && (
            <button
              onClick={onBack}
              className="md:hidden p-1.5 -ml-1 rounded-lg text-slate-300 hover:bg-white/10 cursor-pointer"
              aria-label="Back to chats"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
          )}
          <div className="relative shrink-0">
            <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-cyan-600 to-blue-500 flex items-center justify-center font-bold text-white">
              {contactName.charAt(0).toUpperCase()}
            </div>
            <span
              className={`absolute bottom-0 right-0 w-3 h-3 rounded-full border-2 border-slate-900 ${
                isOnline ? 'bg-emerald-400' : 'bg-slate-500'
              }`}
            />
          </div>
          <div className="min-w-0">
            <h3 className="font-semibold text-slate-100 text-sm truncate">{contactName}</h3>
            <p className={`text-[11px] ${isTyping ? 'text-cyan-300 italic' : isOnline ? 'text-emerald-400' : 'text-slate-500'}`}>
              {statusLine}
            </p>
          </div>
        </div>

        {/* Visual indicator only - not a claim of end-to-end encryption */}
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[11px] font-mono shrink-0">
          <Lock className="w-3 h-3" />
          <span className="hidden sm:inline">Secure connection</span>
        </div>
      </div>

      {connectionState !== 'connected' && (
        <div className="px-4 py-1.5 bg-amber-500/10 border-b border-amber-500/20 text-amber-300 text-[11px] flex items-center gap-2">
          <WifiOff className="w-3.5 h-3.5" />
          <span>{connectionState === 'reconnecting' ? 'Reconnecting… messages will send when connected.' : 'Offline'}</span>
        </div>
      )}

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-3 sm:px-6 py-4 space-y-1 cyber-bg">
        {loading ? (
          <div className="h-full flex items-center justify-center">
            <LoadingSpinner size="md" text="Loading conversation..." />
          </div>
        ) : error ? (
          <div className="h-full flex flex-col items-center justify-center gap-2 text-xs text-slate-400">
            <span>{error}</span>
            <button onClick={loadMessages} className="px-3 py-1 rounded bg-white/10 hover:bg-white/20 cursor-pointer">
              Retry
            </button>
          </div>
        ) : messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center text-slate-500">
            <Lock className="w-6 h-6 mb-2 text-cyan-400/60" />
            <p className="text-xs">Start a conversation with {contactName}.</p>
          </div>
        ) : (
          messages.map((msg, i) => {
            const isMine = msg.sender_id === myId;
            const prev = messages[i - 1];
            const showDay = !prev || formatDay(prev.timestamp) !== formatDay(msg.timestamp);
            const grouped = prev && prev.sender_id === msg.sender_id && !showDay;
            return (
              <React.Fragment key={msg.client_id || msg.message_id}>
                {showDay && (
                  <div className="flex justify-center my-3">
                    <span className="px-3 py-1 rounded-full bg-slate-800/80 border border-white/5 text-[10px] text-slate-400 font-mono">
                      {formatDay(msg.timestamp)}
                    </span>
                  </div>
                )}
                {/* Sent = right, received = left - for every user */}
                <div className={`flex ${isMine ? 'justify-end' : 'justify-start'} ${grouped ? 'mt-0.5' : 'mt-2'}`}>
                  <div
                    className={`relative max-w-[78%] sm:max-w-[65%] px-3 pt-2 pb-1.5 rounded-2xl text-sm leading-relaxed shadow ${
                      isMine
                        ? 'bg-gradient-to-br from-blue-600 to-cyan-600 text-white rounded-br-md'
                        : 'bg-slate-800/90 text-slate-100 border border-white/10 rounded-bl-md'
                    }`}
                  >
                    <p className="whitespace-pre-wrap break-words pr-14">{msg.content}</p>
                    <span
                      className={`absolute bottom-1 right-2 flex items-center gap-1 text-[10px] ${
                        isMine ? 'text-white/70' : 'text-slate-400'
                      }`}
                    >
                      {formatTime(msg.timestamp)}
                      {isMine && <Ticks msg={msg} />}
                    </span>
                  </div>
                </div>
              </React.Fragment>
            );
          })
        )}

        {isTyping && (
          <div className="flex justify-start mt-2">
            <div className="px-4 py-3 rounded-2xl rounded-bl-md bg-slate-800/90 border border-white/10 flex gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-bounce [animation-delay:-0.3s]" />
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-bounce [animation-delay:-0.15s]" />
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-bounce" />
            </div>
          </div>
        )}
      </div>

      {/* Composer */}
      <form onSubmit={handleSend} className="p-3 bg-slate-900/90 border-t border-white/10 flex items-center gap-2">
        <input
          ref={inputRef}
          type="text"
          value={inputText}
          onChange={(e) => {
            setInputText(e.target.value);
            if (e.target.value) sendTyping(conversationId);
          }}
          placeholder="Type a message"
          maxLength={5000}
          className="flex-1 glass-input rounded-full px-4 py-2.5 text-sm text-slate-100 placeholder:text-slate-500"
        />
        <button
          type="submit"
          disabled={!inputText.trim()}
          className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center cursor-pointer transition-all"
          aria-label="Send"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
};
