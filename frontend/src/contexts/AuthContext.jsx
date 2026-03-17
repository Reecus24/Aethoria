import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem('aeth_token'));
  const [loading, setLoading] = useState(true);

  // Axios interceptor: attach token to every request
  useEffect(() => {
    const interceptor = axios.interceptors.request.use((config) => {
      const t = localStorage.getItem('aeth_token');
      if (t) {
        config.headers.Authorization = `Bearer ${t}`;
      }
      return config;
    });
    return () => axios.interceptors.request.eject(interceptor);
  }, []);

  // Bootstrap: restore session on page load
  const restoreSession = useCallback(async () => {
    const storedToken = localStorage.getItem('aeth_token');
    if (!storedToken) {
      setLoading(false);
      return;
    }
    try {
      const res = await axios.get(`${API}/me`, {
        headers: { Authorization: `Bearer ${storedToken}` },
      });
      setUser(res.data.user);
      setToken(storedToken);
    } catch (err) {
      // Only clear on explicit 401 auth failure — preserve token on network errors
      if (err.response && err.response.status === 401) {
        localStorage.removeItem('aeth_token');
        setToken(null);
        setUser(null);
      }
      // On network/timeout errors, keep the token so user stays logged in on retry
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    restoreSession();
  }, [restoreSession]);

  const loginWithData = (responseData) => {
    const { token: newToken, user: userData } = responseData;
    localStorage.setItem('aeth_token', newToken);
    setToken(newToken);
    setUser(userData);
  };

  const logout = async () => {
    try {
      await axios.post(`${API}/auth/logout`);
    } catch { /* ignore */ }
    localStorage.removeItem('aeth_token');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, loginWithData, logout, setUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};
