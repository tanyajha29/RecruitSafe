import React, { createContext, useState, useEffect, useContext } from 'react';
import authService from '../services/authService';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in on initial load
    const initializeAuth = () => {
      try {
        const storedUser = localStorage.getItem('user') || sessionStorage.getItem('user');
        const storedToken = localStorage.getItem('token') || sessionStorage.getItem('token');
        
        if (storedUser && storedToken) {
          setUser(JSON.parse(storedUser));
        }
      } catch (error) {
        console.error('Failed to parse stored user session:', error);
        localStorage.removeItem('user');
        sessionStorage.removeItem('user');
        localStorage.removeItem('token');
        sessionStorage.removeItem('token');
      } finally {
        setLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const loginUser = async (email, password, rememberMe) => {
    setLoading(true);
    try {
      const data = await authService.login(email, password);
      const { access_token, user: loggedUser } = data;
      
      setUser(loggedUser);
      
      const storage = rememberMe ? localStorage : sessionStorage;
      storage.setItem('token', access_token);
      storage.setItem('user', JSON.stringify(loggedUser));
      
      return loggedUser;
    } finally {
      setLoading(false);
    }
  };

  const registerUser = async (fullName, email, password) => {
    setLoading(true);
    try {
      const data = await authService.register(fullName, email, password);
      const { access_token, user: newUser } = data;
      
      setUser(newUser);
      
      // Default to session storage on register unless user explicitly checks remember me later
      sessionStorage.setItem('token', access_token);
      sessionStorage.setItem('user', JSON.stringify(newUser));
      
      return newUser;
    } finally {
      setLoading(false);
    }
  };

  const logoutUser = async () => {
    setLoading(true);
    try {
      // Best-effort backend notification
      await authService.logout().catch((err) => console.warn('Backend logout failed:', err));
    } finally {
      setUser(null);
      localStorage.removeItem('token');
      sessionStorage.removeItem('token');
      localStorage.removeItem('user');
      sessionStorage.removeItem('user');
      setLoading(false);
    }
  };

  const value = {
    user,
    setUser,
    loading,
    loginUser,
    registerUser,
    logoutUser,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
