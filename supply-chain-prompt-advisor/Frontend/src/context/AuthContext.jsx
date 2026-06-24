import { createContext, useCallback, useContext, useMemo, useState } from 'react';
import { login as loginRequest } from '../services/authService';

const TOKEN_KEY = 'supply_chain_prompt_token';
const USER_KEY = 'supply_chain_prompt_user';

const AuthContext = createContext(null);

function getStoredUser() {
  const value = localStorage.getItem(USER_KEY);

  if (!value) {
    return null;
  }

  try {
    return JSON.parse(value);
  } catch {
    localStorage.removeItem(USER_KEY);
    return null;
  }
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY));
  const [user, setUser] = useState(getStoredUser);

  const clearAuthStorage = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }, []);

  const login = useCallback(async (credentials) => {
    const response = await loginRequest(credentials);
    const nextToken = response?.token;
    const nextUser = response?.user ?? null;

    if (!nextToken) {
      throw new Error('Login response did not include a token.');
    }

    localStorage.setItem(TOKEN_KEY, nextToken);
    localStorage.setItem(USER_KEY, JSON.stringify(nextUser));
    setToken(nextToken);
    setUser(nextUser);

    return response;
  }, []);

  const logout = useCallback(() => {
    clearAuthStorage();
    setToken(null);
    setUser(null);
  }, [clearAuthStorage]);

  const value = useMemo(
    () => ({
      token,
      user,
      isAuthenticated: Boolean(token),
      login,
      logout,
      clearAuthStorage,
    }),
    [clearAuthStorage, login, logout, token, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider.');
  }

  return context;
}
