import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, UserRole } from '../types';
import { api } from '../services/api';

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<User>;
  register: (name: string, email: string, password: string, role: UserRole) => Promise<User>;
  logout: () => Promise<void>;
  isChild: boolean;
  isParent: boolean;
  isContact: boolean;
  selectedRoleForLogin: UserRole | null;
  setSelectedRoleForLogin: (role: UserRole | null) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    const saved = sessionStorage.getItem('user');
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState<string | null>(() => sessionStorage.getItem('token'));
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedRoleForLogin, setSelectedRoleForLogin] = useState<UserRole | null>(() => {
    const saved = sessionStorage.getItem('selected_role');
    return (saved as UserRole) || null;
  });

  useEffect(() => {
    const verifyUser = async () => {
      const storedToken = sessionStorage.getItem('token');
      if (!storedToken) {
        setLoading(false);
        return;
      }
      try {
        const res = await api.get('/auth/me');
        setUser(res.data.user);
        sessionStorage.setItem('user', JSON.stringify(res.data.user));
      } catch (err) {
        console.error('Failed to verify session', err);
        sessionStorage.removeItem('token');
        sessionStorage.removeItem('user');
        setUser(null);
        setToken(null);
      } finally {
        setLoading(false);
      }
    };
    verifyUser();
  }, []);

  const login = async (email: string, password: string): Promise<User> => {
    const res = await api.post('/auth/login', { email, password });
    const { token: newToken, user: newUser } = res.data;
    setToken(newToken);
    setUser(newUser);
    sessionStorage.setItem('token', newToken);
    sessionStorage.setItem('user', JSON.stringify(newUser));
    return newUser;
  };

  const register = async (name: string, email: string, password: string, role: UserRole): Promise<User> => {
    const res = await api.post('/auth/register', { name, email, password, role });
    const { token: newToken, user: newUser } = res.data;
    setToken(newToken);
    setUser(newUser);
    sessionStorage.setItem('token', newToken);
    sessionStorage.setItem('user', JSON.stringify(newUser));
    return newUser;
  };

  const logout = async () => {
    try {
      if (token) {
        await api.post('/auth/logout');
      }
    } catch (e) {
      console.warn('Logout API error:', e);
    } finally {
      sessionStorage.removeItem('token');
      sessionStorage.removeItem('user');
      setUser(null);
      setToken(null);
    }
  };

  const handleSetSelectedRole = (role: UserRole | null) => {
    setSelectedRoleForLogin(role);
    if (role) {
      sessionStorage.setItem('selected_role', role);
    } else {
      sessionStorage.removeItem('selected_role');
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        login,
        register,
        logout,
        isChild: user?.role === 'CHILD',
        isParent: user?.role === 'PARENT',
        isContact: user?.role === 'CONTACT',
        selectedRoleForLogin,
        setSelectedRoleForLogin: handleSetSelectedRole,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
