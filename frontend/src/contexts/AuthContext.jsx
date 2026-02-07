import { createContext, useState, useEffect, useContext } from 'react';
import client from '../api/client';
import {jwtDecode} from 'jwt-decode';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check token on load
  useEffect(() => {
    const checkUser = async () => {
        const token = localStorage.getItem('token');
        if (token) {
            try {
                // Determine if token is expired? jwtDecode can check exp
                const decoded = jwtDecode(token);
                if (decoded.exp * 1000 < Date.now()) {
                    logout();
                    return;
                }
                // Fetch full profile
                const res = await client.get('/users/me');
                setUser(res.data);
            } catch (error) {
                console.error("Auth Check Failed:", error);
                logout(); // Invalid token
            }
        }
        setLoading(false);
    };
    checkUser();
  }, []);

  const login = async (username, password) => {
    // 1. Get Token
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);
    
    const res = await client.post('/login/access-token', params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    
    const { access_token } = res.data;
    localStorage.setItem('token', access_token);
    
    // 2. Get User Profile
    const profileRes = await client.get('/users/me');
    setUser(profileRes.data);
    return profileRes.data;
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
