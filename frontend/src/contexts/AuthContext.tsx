import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';
import type { User, UserRole } from '../types';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  hasRole: (role: UserRole) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Simulated users matching backend's scaffolded JWT
const SIMULATED_USERS: Record<string, { password: string; role: UserRole }> = {
  admin: { password: 'admin', role: 'admin' },
  manager: { password: 'manager', role: 'manager' },
  analyst: { password: 'analyst', role: 'analyst' },
  viewer: { password: 'viewer', role: 'viewer' },
};

const ROLE_HIERARCHY: Record<UserRole, number> = {
  admin: 4,
  manager: 3,
  analyst: 2,
  viewer: 1,
};

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(() => {
    const stored = localStorage.getItem('auth_user');
    return stored ? JSON.parse(stored) : null;
  });
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('auth_token'));

  const login = useCallback(async (username: string, password: string) => {
    const simUser = SIMULATED_USERS[username];
    if (!simUser || simUser.password !== password) {
      throw new Error('Invalid credentials');
    }

    const fakeToken = btoa(JSON.stringify({ sub: username, role: simUser.role, exp: Date.now() + 86400000 }));
    const newUser: User = { id: username, username, role: simUser.role };

    localStorage.setItem('auth_token', fakeToken);
    localStorage.setItem('auth_user', JSON.stringify(newUser));
    setToken(fakeToken);
    setUser(newUser);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_user');
    setToken(null);
    setUser(null);
  }, []);

  const hasRole = useCallback(
    (requiredRole: UserRole) => {
      if (!user) return false;
      return ROLE_HIERARCHY[user.role] >= ROLE_HIERARCHY[requiredRole];
    },
    [user]
  );

  return (
    <AuthContext.Provider value={{ user, token, isAuthenticated: !!user, login, logout, hasRole }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
