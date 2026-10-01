import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useSocket } from '../../context/SocketContext';
import { Message } from '../../types';
import { api } from '../../services/api';
import { Send, Lock, Circle, Check, CheckCheck } from 'lucide-react';
import { LoadingSpinner } from '../common/States';

interface ChatWindowProps {
  conversationId: string;
  contactName: string;
  contactId?: string;
  contactStatus?: 'online' | 'offline';
}

export const ChatWindow: React.FC<ChatWindowProps> = ({
  conversationId,
  contactName,
  contactId,
  contactStatus: initialStatus = 'offline',
}) => {
  const { user } = useAuth();
  const { sendMessage, sendTyping, sendRead, latestMessage, typingMap, onlineUsers } = useSocket();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  // Check live online status from socket onlineUsers
  const isOnline = contactId ? onlineUsers.includes(contactId) : initialStatus === 'online';
  const isTyping = typingMap[conversationId] !== undefined;

  // Load message history
  useEffect(() => {
    let isMounted = true;
    const loadMessages = async () => {
      try {
        setLoading(true);
        const res = await api.get(`/messages/${conversationId}?limit=100`);
        if (isMounted) {
          setMessages(res.data.messages || []);
          sendRead(conversationId);
        }
      } catch (err) {
        console.error('Failed to load messages', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    loadMessages();
    return () => {
      isMounted = false;
    };
  }, [conversationId, sendRead]);

  // Append new messages received via WebSocket
  useEffect(() => {
    if (latestMessage && latestMessage.conversation_id === conversationId) {
      setMessages((prev) => {
        // Prevent duplicate messages if already present
        if (prev.some((m) => m.message_id === latestMessage.message_id)) {
          return prev;
        }
        return [...prev, latestMessage];
      });
      // Mark as read if user is the receiver
      if (latestMessage.receiver_id === user?._id) {
        sendRead(conversationId);
      }
    }
  }, [latestMessage, conversationId, user?._id, sendRead]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const handleSend = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const trimmed = inputText.trim();
    if (!trimmed) return;

    sendMessage(conversationId, trimmed);
    setInputText('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    } else {
      sendTyping(conversationId);
    }
  };

  const formatTime = (ts: string) => {
    try {
      const date = new Date(ts);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return '';
    }
  };

  return (
    <div className="flex flex-col h-full bg-[#0d0d15] rounded-xl border border-white/10 overflow-hidden shadow-2xl">
      {/* Header */}
      <div className="px-5 py-3.5 bg-slate-900/80 border-b border-white/10 flex items-center justify-between backdrop-blur-md">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-cyan-600 to-blue-500 flex items-center justify-center font-bold text-white shadow-md text-sm">
              {contactName.charAt(0).toUpperCase()}
            </div>
            <span
              className={`absolute bottom-0 right-0 w-3 h-3 rounded-full border-2 border-[#0d0d15] ${
                isOnline ? 'bg-emerald-400' : 'bg-slate-500'
              }`}
            />
          </div>
          <div>
            <h3 className="font-semibold text-slate-100 text-sm">{contactName}</h3>
            <div className="flex items-center gap-1.5 text-[11px] text-slate-400">
              <Circle className={`w-2 h-2 ${isOnline ? 'fill-emerald-400 text-emerald-400' : 'fill-slate-500 text-slate-500'}`} />
              <span>{isOnline ? 'Active Now' : 'Offline'}</span>
            </div>
          </div>
        </div>

        {/* Security Indicator Requirement #49 */}
        <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-mono">
          <Lock className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Secure channel</span>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3 cyber-bg">
        {loading ? (
          <div className="h-full flex items-center justify-center">
            <LoadingSpinner size="md" text="Loading secure conversation..." />
          </div>
        ) : messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-6 text-slate-500">
            <div className="w-12 h-12 rounded-full bg-white/5 flex items-center justify-center mb-2 text-cyan-400">
              <Lock className="w-5 h-5 opacity-60" />
            </div>
            <p className="text-xs">No messages yet. Send a message to start communicating.</p>
          </div>
        ) : (
          messages.map((msg) => {
            const isMine = msg.sender_id === user?._id;
            return (
              <div
                key={msg.message_id || Math.random()}
                className={`flex flex-col ${isMine ? 'items-end' : 'items-start'}`}
              >
                <div
                  className={`max-w-[75%] px-4 py-2.5 rounded-2xl text-xs sm:text-sm leading-relaxed ${
                    isMine
                      ? 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-br-none shadow-[0_2px_10px_rgba(0,168,255,0.2)]'
                      : 'glass-card bg-slate-800/80 text-slate-200 rounded-bl-none border border-white/10'
                  }`}
                >
                  <p className="break-words select-text">{msg.content}</p>
                </div>
                <div className="flex items-center gap-1 mt-1 px-1 text-[10px] text-slate-500 font-mono">
                  <span>{formatTime(msg.timestamp)}</span>
                  {isMine && (
                    <span>
                      {msg.delivery_status === 'read' ? (
                        <CheckCheck className="w-3 h-3 text-cyan-400" />
                      ) : (
                        <Check className="w-3 h-3 text-slate-500" />
                      )}
                    </span>
                  )}
                </div>
              </div>
            );
          })
        )}

        {/* Typing indicator */}
        {isTyping && (
          <div className="flex items-center gap-2 text-xs text-cyan-400 italic bg-white/5 px-3 py-1.5 rounded-full w-fit animate-pulse border border-white/5">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-bounce" />
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-bounce delay-100" />
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-bounce delay-200" />
            <span className="ml-1 text-[11px] font-mono">{contactName} is typing...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <form onSubmit={handleSend} className="p-3 bg-slate-900/90 border-t border-white/10 flex items-center gap-2">
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={`Message ${contactName}...`}
          className="flex-1 glass-input rounded-xl px-4 py-2.5 text-xs sm:text-sm text-slate-100 placeholder:text-slate-500 focus:ring-1 focus:ring-cyan-500"
        />
        <button
          type="submit"
          disabled={!inputText.trim()}
          className="p-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white disabled:opacity-40 disabled:cursor-not-allowed shadow-[0_0_12px_rgba(0,168,255,0.25)] transition-all flex items-center justify-center cursor-pointer"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
};
