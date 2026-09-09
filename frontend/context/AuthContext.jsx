import { createContext, useContext, useState } from 'react';
import api from '../api/cloud-vault';

const AuthContext = createContext(null);
export const useAuth = () => useContext(AuthContext);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);

  const login = async (email, password) => {
    const { data } = await api.post('/api/auth/login', { email, password });
    localStorage.setItem('token', data.access_token);
    const me = await api.get('/api/auth/me');
    setUser(me.data);
  };

  const signup = async (email, password, full_name) => {
    await api.post('/api/auth/signup', { email, password, full_name });
    await login(email, password); // auto-login after signup
  };

  const logout = async () => {
    try { await api.post('/api/auth/logout'); } catch { /* token already dead */ }
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}