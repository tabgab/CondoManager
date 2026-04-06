import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import type { User } from '../types/auth';

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

interface AuthActions {
  setUser: (user: User | null) => void;
  setTokens: (accessToken: string | null, refreshToken: string | null) => void;
  setAuthenticated: (authenticated: boolean) => void;
  setLoading: (loading: boolean) => void;
  logout: () => void;
  login: (email: string, password: string) => Promise<void>;
  refreshAccessToken: () => Promise<void>;
  checkAuth: () => Promise<void>;
}

type AuthStore = AuthState & AuthActions;

const initialState: AuthState = {
  user: null,
  accessToken: null,
  refreshToken: null,
  isAuthenticated: false,
  isLoading: false,
};

export const useAuthStore = create<AuthStore, [['zustand/persist', unknown], ['zustand/immer', never]]>(
  persist(
    immer((set, get) => ({
      ...initialState,

      setUser: (user) => {
        set((state) => {
          state.user = user;
        });
      },

      setTokens: (accessToken, refreshToken) => {
        set((state) => {
          state.accessToken = accessToken;
          state.refreshToken = refreshToken;
          state.isAuthenticated = !!accessToken;
        });
      },

      setAuthenticated: (authenticated) => {
        set((state) => {
          state.isAuthenticated = authenticated;
        });
      },

      setLoading: (loading) => {
        set((state) => {
          state.isLoading = loading;
        });
      },

      logout: () => {
        set((state) => {
          state.user = null;
          state.accessToken = null;
          state.refreshToken = null;
          state.isAuthenticated = false;
          state.isLoading = false;
        });
        // Clear persisted storage
        localStorage.removeItem('auth-storage');
      },

      // API integration methods (async, not affecting state directly in tests)
      login: async (_email: string, _password: string): Promise<void> => {
        // Placeholder for API integration
        // Full implementation will call API client
        get().setLoading(true);
        try {
          // API call will go here
          // const response = await api.post('/auth/login', { email, password });
          // get().setUser(response.data.user);
          // get().setTokens(response.data.access_token, response.data.refresh_token);
        } finally {
          get().setLoading(false);
        }
      },

      refreshAccessToken: async (): Promise<void> => {
        const { refreshToken } = get();
        if (!refreshToken) {
          get().logout();
          return;
        }
        // Placeholder for API integration
        // const response = await api.post('/auth/refresh', { refresh_token: refreshToken });
        // get().setTokens(response.data.access_token, response.data.refresh_token);
      },

      checkAuth: async (): Promise<void> => {
        const { accessToken } = get();
        if (!accessToken) {
          get().logout();
          return;
        }
        // Placeholder for API integration
        // try {
        //   const response = await api.get('/auth/me');
        //   get().setUser(response.data);
        // } catch {
        //   get().logout();
        // }
      },
    })),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
