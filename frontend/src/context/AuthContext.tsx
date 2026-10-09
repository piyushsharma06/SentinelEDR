/**
 * Authentication Context for SentinelEDR
 */

import React, { createContext, useContext, useState, useEffect } from 'react';
import { AnalystUser } from '../types';
import { api } from '../api/client';

interface AuthContextType {
  user: AnalystUser | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AnalystUser | null>(() => {
    const saved = localStorage.getItem('sentinel_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('sentinel_token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const verifyToken = async () => {
      if (token) {
        try {
          const profile = await api.getMe();
          setUser(profile);
          localStorage.setItem('sentinel_user', JSON.stringify(profile));
        } catch {
          logout();
        }
      }
      setLoading(false);
    };

    verifyToken();
  }, [token]);

  const login = async (username: string, password: string) => {
    const response = await api.login(username, password);
    setToken(response.access_token);
    setUser(response.user);
    localStorage.setItem('sentinel_token', response.access_token);
    localStorage.setItem('sentinel_user', JSON.stringify(response.user));
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('sentinel_token');
    localStorage.removeItem('sentinel_user');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token,
        loading,
        login,
        logout,
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
