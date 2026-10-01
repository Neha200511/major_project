import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../../services/api';
import { Conversation } from '../../types';
import { ChatWindow } from '../../components/chat/ChatWindow';
import { ArrowLeft } from 'lucide-react';
import { LoadingSpinner } from '../../components/common/States';

export const ContactChat: React.FC = () => {
  const { conversationId } = useParams<{ conversationId: string }>();
  const navigate = useNavigate();
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchConv = async () => {
      if (!conversationId) return;
      try {
        setLoading(true);
        const res = await api.get(`/conversations`);
        const found = (res.data.conversations || []).find(
          (c: Conversation) => c.conversation_id === conversationId
        );
        setConversation(found || null);
      } catch (err) {
        console.error('Failed to load contact chat', err);
      } finally {
        setLoading(false);
      }
    };

    fetchConv();
  }, [conversationId]);

  if (loading) {
    return <LoadingSpinner size="lg" text="Connecting to conversation channel..." />;
  }

  if (!conversationId || !conversation) {
    return (
      <div className="text-center p-8 glass-card">
        <p className="text-sm text-slate-300 mb-4">Conversation channel not found or access denied.</p>
        <button
          onClick={() => navigate('/contact')}
          className="px-4 py-2 rounded-lg bg-emerald-600 text-white text-xs font-semibold"
        >
          Return to Dashboard
        </button>
      </div>
    );
  }

  return (
    <div className="h-[calc(100vh-10rem)] flex flex-col max-w-4xl mx-auto">
      <div className="mb-3">
        <button
          onClick={() => navigate('/contact')}
          className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-emerald-400 transition-colors cursor-pointer"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to conversations</span>
        </button>
      </div>

      <div className="flex-1 min-h-0">
        <ChatWindow
          conversationId={conversationId}
          contactName={conversation.contact_name || 'Child'}
          contactId={conversation.contact_id}
          contactStatus={conversation.contact_status}
        />
      </div>
    </div>
  );
};
