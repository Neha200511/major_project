import React, { createContext, useContext, useState, useEffect, useRef, useCallback } from 'react';
import { useAuth } from './AuthContext';
import { Message, Alert } from '../types';

type ConnectionState = 'connected' | 'reconnecting' | 'offline';

interface SocketContextType {
  connectionState: ConnectionState;
  onlineUsers: string[];
  sendMessage: (conversationId: string, content: string) => void;
  sendTyping: (conversationId: string) => void;
  sendRead: (conversationId: string) => void;
  latestMessage: Message | null;
  typingMap: Record<string, string>; // conversation_id -> user_id
  newParentAlert: Alert | null;
  dismissParentAlert: () => void;
}

const SocketContext = createContext<SocketContextType | undefined>(undefined);

export const SocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, token, isParent } = useAuth();
  const [connectionState, setConnectionState] = useState<ConnectionState>('offline');
  const [onlineUsers, setOnlineUsers] = useState<string[]>([]);
  const [latestMessage, setLatestMessage] = useState<Message | null>(null);
  const [typingMap, setTypingMap] = useState<Record<string, string>>({});
  const [newParentAlert, setNewParentAlert] = useState<Alert | null>(null);

  const chatWsRef = useRef<WebSocket | null>(null);
  const alertWsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<any>(null);
  const typingTimeoutRef = useRef<Record<string, any>>({});

  // Setup WebSocket connection
  const connectSockets = useCallback(() => {
    if (!token || !user) {
      if (chatWsRef.current) chatWsRef.current.close();
      if (alertWsRef.current) alertWsRef.current.close();
      setConnectionState('offline');
      return;
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host; // Uses Vite dev proxy or production host

    // Chat WebSocket
    const chatUrl = `${protocol}//${host}/ws/chat/${token}`;
    const ws = new WebSocket(chatUrl);

    ws.onopen = () => {
      setConnectionState('connected');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'message' && data.message) {
          setLatestMessage(data.message);
        } else if (data.type === 'typing') {
          const { conversation_id, user_id } = data;
          setTypingMap((prev) => ({ ...prev, [conversation_id]: user_id }));
          
          if (typingTimeoutRef.current[conversation_id]) {
            clearTimeout(typingTimeoutRef.current[conversation_id]);
          }
          typingTimeoutRef.current[conversation_id] = setTimeout(() => {
            setTypingMap((prev) => {
              const copy = { ...prev };
              delete copy[conversation_id];
              return copy;
            });
          }, 3000);
        } else if (data.type === 'online_users') {
          setOnlineUsers(data.users || []);
        } else if (data.type === 'status') {
          const { user_id, status } = data;
          setOnlineUsers((prev) => {
            if (status === 'online') {
              return prev.includes(user_id) ? prev : [...prev, user_id];
            } else {
              return prev.filter((id) => id !== user_id);
            }
          });
        } else if (data.type === 'alert' && data.alert) {
          setNewParentAlert(data.alert);
        }
      } catch (err) {
        console.error('Failed to parse WebSocket message', err);
      }
    };

    ws.onclose = () => {
      setConnectionState('offline');
      // Attempt reconnect after 3 seconds
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = setTimeout(() => {
        setConnectionState('reconnecting');
        connectSockets();
      }, 3000);
    };

    ws.onerror = () => {
      ws.close();
    };

    chatWsRef.current = ws;

    // Parent Alert WebSocket (only for parents)
    if (isParent) {
      const alertUrl = `${protocol}//${host}/ws/alerts/${token}`;
      const alertWs = new WebSocket(alertUrl);

      alertWs.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'alert' && data.alert) {
            setNewParentAlert(data.alert);
          }
        } catch (err) {
          console.error('Failed to parse alert socket data', err);
        }
      };

      alertWsRef.current = alertWs;
    }
  }, [token, user, isParent]);

  useEffect(() => {
    connectSockets();

    return () => {
      if (chatWsRef.current) chatWsRef.current.close();
      if (alertWsRef.current) alertWsRef.current.close();
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
    };
  }, [connectSockets]);

  const sendMessage = useCallback((conversationId: string, content: string) => {
    if (chatWsRef.current && chatWsRef.current.readyState === WebSocket.OPEN) {
      chatWsRef.current.send(
        JSON.stringify({
          type: 'message',
          conversation_id: conversationId,
          content,
        })
      );
    }
  }, []);

  const sendTyping = useCallback((conversationId: string) => {
    if (chatWsRef.current && chatWsRef.current.readyState === WebSocket.OPEN) {
      chatWsRef.current.send(
        JSON.stringify({
          type: 'typing',
          conversation_id: conversationId,
        })
      );
    }
  }, []);

  const sendRead = useCallback((conversationId: string) => {
    if (chatWsRef.current && chatWsRef.current.readyState === WebSocket.OPEN) {
      chatWsRef.current.send(
        JSON.stringify({
          type: 'read',
          conversation_id: conversationId,
        })
      );
    }
  }, []);

  const dismissParentAlert = useCallback(() => {
    setNewParentAlert(null);
  }, []);

  return (
    <SocketContext.Provider
      value={{
        connectionState,
        onlineUsers,
        sendMessage,
        sendTyping,
        sendRead,
        latestMessage,
        typingMap,
        newParentAlert,
        dismissParentAlert,
      }}
    >
      {children}
    </SocketContext.Provider>
  );
};

export const useSocket = () => {
  const context = useContext(SocketContext);
  if (!context) {
    throw new Error('useSocket must be used within a SocketProvider');
  }
  return context;
};
