// @ts-nocheck
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
  _hasHydrated: boolean;
}

interface AuthActions {
  setUser: (user: User | null) => void;
  setTokens: (accessToken: string | null, refreshToken: string | null) => void;
  setAuthenticated: (authenticated: boolean) => void;
  setLoading: (loading: boolean) => void;
  setHasHydrated: (state: boolean) => void;
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
  _hasHydrated: false,
};

export const useAuthStore = create<AuthStore, [['zustand/persist', unknown], ['zustand/immer', never]]>(
  persist(
    immer((set, get) => ({
      ...initialState,

      setHasHydrated: (state) => {
        set((s) => {
          s._hasHydrated = state;
        });
      },

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

      login: async (_email: string, _password: string): Promise<void> => {
        get().setLoading(true);
        try {
          // Full login implementation is in Login.tsx using api directly
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
      },

      checkAuth: async (): Promise<void> => {
        const { accessToken } = get();
        if (!accessToken) {
          get().logout();
          return;
        }
        // Token exists - user is considered authenticated
        // Full /auth/me validation happens via api interceptors
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
      onRehydrateStorage: () => (state) => {
        // Called after Zustand rehydrates from localStorage
        if (state) {
          state.setHasHydrated(true);
        }
      },
    }
  )
);
