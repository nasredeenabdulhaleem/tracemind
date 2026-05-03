import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      setLoading(false);
      return;
    }

    try {
      const response = await authAPI.getMe();
      setUser(response.data);
    } catch (err) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    } finally {
      setLoading(false);
    }
  };

  const extractError = (err, fallback) => {
    const detail = err.response?.data?.detail;
    if (!detail) return fallback;
    // Pydantic 422 returns detail as an array of validation errors
    if (Array.isArray(detail)) {
      return detail.map((e) => e.msg || String(e)).join('; ');
    }
    return String(detail);
  };

  const login = async (email, password) => {
    setError(null);
    try {
      const response = await authAPI.login({ email, password });
      const { access_token, user: userData } = response.data;

      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));
      setUser(userData);

      return { success: true };
    } catch (err) {
      const message = extractError(err, 'Login failed');
      setError(message);
      return { success: false, error: message };
    }
  };

  const register = async (userData) => {
    setError(null);
    try {
      await authAPI.register(userData);
      return { success: true };
    } catch (err) {
      const message = extractError(err, 'Registration failed');
      setError(message);
      return { success: false, error: message };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  const value = {
    user,
    loading,
    error,
    login,
    register,
    logout,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Made with Bob
