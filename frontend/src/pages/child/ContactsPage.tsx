import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../../services/api';
import { User, Conversation } from '../../types';
import { GlassCard } from '../../components/common/GlassCard';
import { LoadingSpinner, EmptyState } from '../../components/common/States';
import { Users, MessageSquare, Circle } from 'lucide-react';
import { useSocket } from '../../context/SocketContext';

export const ContactsPage: React.FC = () => {
  const [contacts, setContacts] = useState<User[]>([]);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const { onlineUsers } = useSocket();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [contactsRes, convsRes] = await Promise.all([
          api.get('/users/contacts'),
          api.get('/conversations'),
        ]);
        setContacts(contactsRes.data.contacts || []);
        setConversations(convsRes.data.conversations || []);
      } catch (err) {
        console.error('Failed to load contacts', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const openChatForContact = (contactId: string) => {
    const conv = conversations.find((c) => c.participants.includes(contactId));
    if (conv) {
      navigate(`/child/chat/${conv.conversation_id}`);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="flex items-center justify-between pb-3 border-b border-white/10">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <Users className="w-5 h-5 text-cyan-400" />
            <span>Approved Contacts</span>
          </h1>
          <p className="text-xs text-slate-400">
            People you can safely communicate with in the platform
          </p>
        </div>
        <span className="text-xs font-mono text-slate-500">{contacts.length} Total Contacts</span>
      </div>

      {loading ? (
        <LoadingSpinner size="lg" text="Loading contacts..." />
      ) : contacts.length === 0 ? (
        <EmptyState title="No Contacts Found" description="You currently have no contacts assigned." />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {contacts.map((contact) => {
            const isOnline = onlineUsers.includes(contact._id);
            return (
              <GlassCard key={contact._id} hover className="p-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="relative">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-cyan-600 to-blue-500 flex items-center justify-center font-bold text-white text-sm">
                      {contact.name.charAt(0).toUpperCase()}
                    </div>
                    <span
                      className={`absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full border-2 border-[#0a0a0f] ${
                        isOnline ? 'bg-emerald-400' : 'bg-slate-500'
                      }`}
                    />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-100 text-xs sm:text-sm">{contact.name}</h3>
                    <div className="flex items-center gap-1.5 text-[10px] text-slate-400">
                      <Circle
                        className={`w-1.5 h-1.5 ${
                          isOnline ? 'fill-emerald-400 text-emerald-400' : 'fill-slate-500 text-slate-500'
                        }`}
                      />
                      <span>{isOnline ? 'Online' : 'Offline'}</span>
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => openChatForContact(contact._id)}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 text-xs font-medium transition-colors cursor-pointer"
                >
                  <MessageSquare className="w-3.5 h-3.5" />
                  <span>Chat</span>
                </button>
              </GlassCard>
            );
          })}
        </div>
      )}
    </div>
  );
};
