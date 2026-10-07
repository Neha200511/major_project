import React, { createContext, useContext, useState, useEffect, useRef, useCallback } from 'react';
import { useAuth } from './AuthContext';
import type { Message, Alert } from '../types';

type ConnectionState = 'connected' | 'reconnecting' | 'offline';

/** Every server event is broadcast to subscribers so no message is ever dropped. */
export type SocketEvent =
  | { type: 'message'; message: Message; client_id?: string }
  | { type: 'read'; conversation_id: string; user_id: string }
  | { type: 'delivered'; conversation_id: string; user_id: string }
  | { type: 'typing'; conversation_id: string; user_id: string }
  | { type: 'status'; user_id: string; status: 'online' | 'offline' }
  | { type: 'unread_count'; conversation_id: string; count: number }
  | { type: 'online_users'; users: string[] }
  | { type: 'alert'; alert: Alert }
  | { type: 'connected' };

type Listener = (event: SocketEvent) => void;

interface SocketContextType {
  connectionState: ConnectionState;
  onlineUsers: string[];
  isUserOnline: (userId?: string) => boolean;
  sendMessage: (conversationId: string, content: string, clientId?: string) => void;
  sendTyping: (conversationId: string) => void;
  sendRead: (conversationId: string) => void;
  subscribe: (listener: Listener) => () => void;
  typingMap: Record<string, string>; // conversation_id -> user_id
  unreadMap: Record<string, number>; // conversation_id -> count
  newParentAlert: Alert | null;
  dismissParentAlert: () => void;
}

const SocketContext = createContext<SocketContextType | undefined>(undefined);

export const SocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { token, user } = useAuth();
  const userId = user?._id;
  const isParent = user?.role === 'PARENT';

  const [connectionState, setConnectionState] = useState<ConnectionState>('offline');
  const [onlineUsers, setOnlineUsers] = useState<string[]>([]);
  const [typingMap, setTypingMap] = useState<Record<string, string>>({});
  const [unreadMap, setUnreadMap] = useState<Record<string, number>>({});
  const [newParentAlert, setNewParentAlert] = useState<Alert | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const alertWsRef = useRef<WebSocket | null>(null);
  const listenersRef = useRef<Set<Listener>>(new Set());
  const queueRef = useRef<string[]>([]);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pingTimer = useRef<ReturnType<typeof setInterval> | null>(null);
  const attemptsRef = useRef(0);
  const typingTimers = useRef<Record<string, ReturnType<typeof setTimeout>>>({});
  const lastTypingSent = useRef<Record<string, number>>({});

  const emit = useCallback((event: SocketEvent) => {
    listenersRef.current.forEach((l) => {
      try {
        l(event);
      } catch (e) {
        console.error('Socket listener error', e);
      }
    });
  }, []);

  const subscribe = useCallback((listener: Listener) => {
    listenersRef.current.add(listener);
    return () => {
      listenersRef.current.delete(listener);
    };
  }, []);

  /** Send immediately if open, otherwise queue until the socket reconnects. */
  const rawSend = useCallback((payload: object, queueIfClosed = true) => {
    const data = JSON.stringify(payload);
    const ws = wsRef.current;
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(data);
    } else if (queueIfClosed) {
      queueRef.current.push(data);
    }
  }, []);

  useEffect(() => {
    if (!token || !userId) {
      setConnectionState('offline');
      setOnlineUsers([]);
      return;
    }

    let disposed = false; // true once this effect is cleaned up -> never reconnect
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;

    const handleEvent = (data: any) => {
      switch (data.type) {
        case 'message':
          emit(data);
          break;
        case 'read':
        case 'delivered':
          emit(data);
          break;
        case 'typing': {
          const cid = data.conversation_id;
          setTypingMap((prev) => ({ ...prev, [cid]: data.user_id }));
          if (typingTimers.current[cid]) clearTimeout(typingTimers.current[cid]);
          typingTimers.current[cid] = setTimeout(() => {
            setTypingMap((prev) => {
              const copy = { ...prev };
              delete copy[cid];
              return copy;
            });
          }, 2500);
          emit(data);
          break;
        }
        case 'online_users':
          setOnlineUsers(data.users || []);
          emit(data);
          break;
        case 'status':
          setOnlineUsers((prev) =>
            data.status === 'online'
              ? prev.includes(data.user_id) ? prev : [...prev, data.user_id]
              : prev.filter((id) => id !== data.user_id)
          );
          emit(data);
          break;
        case 'unread_count':
          setUnreadMap((prev) => ({ ...prev, [data.conversation_id]: data.count }));
          emit(data);
          break;
        case 'alert':
          if (data.alert) setNewParentAlert(data.alert);
          emit(data);
          break;
        default:
          break;
      }
    };

    const connect = () => {
      if (disposed) return;
      const ws = new WebSocket(`${protocol}//${host}/ws/chat/${token}`);
      wsRef.current = ws;

      ws.onopen = () => {
        if (disposed) return;
        attemptsRef.current = 0;
        setConnectionState('connected');
        // Flush anything typed while reconnecting
        const pending = queueRef.current.splice(0);
        pending.forEach((p) => ws.send(p));
        // Keep-alive
        if (pingTimer.current) clearInterval(pingTimer.current);
        pingTimer.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify({ type: 'ping' }));
        }, 25000);
        emit({ type: 'connected' });
      };

      ws.onmessage = (event) => {
        try {
          handleEvent(JSON.parse(event.data));
        } catch (err) {
          console.error('Failed to parse WebSocket message', err);
        }
      };

      ws.onclose = (ev) => {
        if (pingTimer.current) clearInterval(pingTimer.current);
        if (disposed) return;
        if (ev.code === 4001) {
          setConnectionState('offline');
          return; // invalid token: do not retry
        }
        setConnectionState('reconnecting');
        const delay = Math.min(1000 * 2 ** attemptsRef.current, 10000);
        attemptsRef.current += 1;
        reconnectTimer.current = setTimeout(connect, delay);
      };

      ws.onerror = () => {
        // onclose will follow and handle reconnection
      };
    };

    connect();

    // Dedicated parent alert channel
    if (isParent) {
      const alertWs = new WebSocket(`${protocol}//${host}/ws/alerts/${token}`);
      alertWs.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'alert' && data.alert) setNewParentAlert(data.alert);
        } catch {
          /* ignore */
        }
      };
      alertWsRef.current = alertWs;
    }

    return () => {
      disposed = true;
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      if (pingTimer.current) clearInterval(pingTimer.current);
      wsRef.current?.close();
      wsRef.current = null;
      alertWsRef.current?.close();
      alertWsRef.current = null;
    };
    // Reconnect only when the logged-in identity changes
  }, [token, userId, isParent, emit]);

  const sendMessage = useCallback(
    (conversationId: string, content: string, clientId?: string) => {
      rawSend({ type: 'message', conversation_id: conversationId, content, client_id: clientId });
    },
    [rawSend]
  );

  const sendTyping = useCallback(
    (conversationId: string) => {
      // Throttle typing events to one every 1.5s
      const now = Date.now();
      if (now - (lastTypingSent.current[conversationId] || 0) < 1500) return;
      lastTypingSent.current[conversationId] = now;
      rawSend({ type: 'typing', conversation_id: conversationId }, false);
    },
    [rawSend]
  );

  const sendRead = useCallback(
    (conversationId: string) => {
      setUnreadMap((prev) => ({ ...prev, [conversationId]: 0 }));
      rawSend({ type: 'read', conversation_id: conversationId });
    },
    [rawSend]
  );

  const isUserOnline = useCallback(
    (id?: string) => (id ? onlineUsers.includes(id) : false),
    [onlineUsers]
  );

  const dismissParentAlert = useCallback(() => setNewParentAlert(null), []);

  return (
    <SocketContext.Provider
      value={{
        connectionState,
        onlineUsers,
        isUserOnline,
        sendMessage,
        sendTyping,
        sendRead,
        subscribe,
        typingMap,
        unreadMap,
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
  if (!context) throw new Error('useSocket must be used within a SocketProvider');
  return context;
};
