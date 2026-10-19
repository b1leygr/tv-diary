import {
  createContext,
  type ReactNode,
  useContext,
  useMemo,
  useSyncExternalStore,
} from 'react';

export interface AuthContext {
  token: string | null;
  authenticated: boolean;
  login: (token: string) => void;
  logout: () => void;
}

const authEvents = new EventTarget();

export const authService = {
  get token(): string | null {
    return localStorage.getItem('token');
  },
  get authenticated(): boolean {
    return !!this.token;
  },
  login(token: string) {
    localStorage.setItem('token', token);
    authEvents.dispatchEvent(new Event('auth-change'));
  },
  logout() {
    localStorage.removeItem('token');
    authEvents.dispatchEvent(new Event('auth-change'));
  },
  subscribe(callback: () => void) {
    authEvents.addEventListener('auth-change', callback);
    window.addEventListener('storage', callback);
    return () => {
      authEvents.removeEventListener('auth-change', callback);
      window.removeEventListener('storage', callback);
    };
  },
  getSnapshot() {
    return localStorage.getItem('token');
  },
};

const AuthContext = createContext<AuthContext | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const token = useSyncExternalStore(
    authService.subscribe,
    authService.getSnapshot,
  );

  const contextValue = useMemo(
    () => ({
      token,
      authenticated: !!token,
      login: authService.login,
      logout: authService.logout,
    }),
    [token],
  );

  return (
    <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
