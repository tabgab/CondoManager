import { describe, it, expect, beforeEach } from 'vitest';
import { act } from '@testing-library/react';

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => { store[key] = value; },
    removeItem: (key: string) => { delete store[key]; },
    clear: () => { store = {}; },
  };
})();

Object.defineProperty(window, 'localStorage', { value: localStorageMock });

// Import types for testing
type UserRole = 'super_admin' | 'manager' | 'employee' | 'owner' | 'tenant';

interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  is_active: boolean;
}

describe('Auth Store', () => {
  beforeEach(() => {
    localStorage.clear();
    // Reset module cache to get fresh store instance
    vi.resetModules();
  });

  it('should initialize as unauthenticated', async () => {
    const { useAuthStore } = await import('./auth');
    const state = useAuthStore.getState();
    
    expect(state.user).toBeNull();
    expect(state.accessToken).toBeNull();
    expect(state.refreshToken).toBeNull();
    expect(state.isAuthenticated).toBe(false);
    expect(state.isLoading).toBe(false);
  });

  it('should login and update state', async () => {
    const { useAuthStore } = await import('./auth');
    const mockUser: User = {
      id: '1',
      email: 'test@example.com',
      first_name: 'Test',
      last_name: 'User',
      role: 'manager',
      is_active: true,
    };

    await act(async () => {
      useAuthStore.getState().setUser(mockUser);
      useAuthStore.getState().setTokens('access-token', 'refresh-token');
    });

    const state = useAuthStore.getState();
    expect(state.user).toEqual(mockUser);
    expect(state.accessToken).toBe('access-token');
    expect(state.refreshToken).toBe('refresh-token');
    expect(state.isAuthenticated).toBe(true);
  });

  it('should logout and clear state', async () => {
    const { useAuthStore } = await import('./auth');
    const mockUser: User = {
      id: '1',
      email: 'test@example.com',
      first_name: 'Test',
      last_name: 'User',
      role: 'manager',
      is_active: true,
    };

    // First, login
    await act(async () => {
      useAuthStore.getState().setUser(mockUser);
      useAuthStore.getState().setTokens('access-token', 'refresh-token');
    });

    // Then logout
    await act(async () => {
      useAuthStore.getState().logout();
    });

    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.accessToken).toBeNull();
    expect(state.refreshToken).toBeNull();
    expect(state.isAuthenticated).toBe(false);
  });

  it('should persist tokens to localStorage', async () => {
    const { useAuthStore } = await import('./auth');
    const mockUser: User = {
      id: '1',
      email: 'test@example.com',
      first_name: 'Test',
      last_name: 'User',
      role: 'manager',
      is_active: true,
    };

    await act(async () => {
      useAuthStore.getState().setUser(mockUser);
      useAuthStore.getState().setTokens('access-token', 'refresh-token');
    });

    expect(localStorage.getItem('auth-storage')).toBeTruthy();
    const stored = JSON.parse(localStorage.getItem('auth-storage')!);
    expect(stored.state.accessToken).toBe('access-token');
    expect(stored.state.refreshToken).toBe('refresh-token');
    expect(stored.state.user).toEqual(mockUser);
  });

  it('should clear localStorage on logout', async () => {
    const { useAuthStore } = await import('./auth');
    
    // Set some data
    localStorage.setItem('auth-storage', JSON.stringify({ state: { user: { id: '1' } } }));

    await act(async () => {
      useAuthStore.getState().logout();
    });

    expect(localStorage.getItem('auth-storage')).toBeNull();
  });

  it('should update authentication status', async () => {
    const { useAuthStore } = await import('./auth');
    
    expect(useAuthStore.getState().isAuthenticated).toBe(false);

    await act(async () => {
      useAuthStore.getState().setAuthenticated(true);
    });

    expect(useAuthStore.getState().isAuthenticated).toBe(true);
  });

  it('should set loading state', async () => {
    const { useAuthStore } = await import('./auth');
    
    expect(useAuthStore.getState().isLoading).toBe(false);

    await act(async () => {
      useAuthStore.getState().setLoading(true);
    });

    expect(useAuthStore.getState().isLoading).toBe(true);
  });
});
