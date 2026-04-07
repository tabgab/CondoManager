import axios, { AxiosError, AxiosResponse, InternalAxiosRequestConfig } from 'axios';
import { useAuthStore } from '../store/auth';
import { API_BASE_URL, IS_PRODUCTION, DEBUG_MODE } from './config';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Log API base URL in development
if (!IS_PRODUCTION) {
  console.log('[API] Base URL:', API_BASE_URL);
}

// Track whether we are currently refreshing to avoid loops
let isRefreshing = false;
let failedQueue: Array<{ resolve: (value: unknown) => void; reject: (reason?: unknown) => void }> = [];

const processQueue = (error: unknown, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

// Request interceptor to attach access token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = useAuthStore.getState().accessToken || localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle 401 and auto-refresh
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Only attempt refresh for 401 errors, not for other errors
    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      // Don't retry login/register/refresh endpoints themselves
      const url = originalRequest.url || '';
      if (url.includes('/auth/login') || url.includes('/auth/register') || url.includes('/auth/refresh')) {
        return Promise.reject(error);
      }

      if (isRefreshing) {
        // Queue this request until refresh is done
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then((token) => {
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${token}`;
          }
          return api(originalRequest);
        }).catch((err) => {
          return Promise.reject(err);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const refreshToken = useAuthStore.getState().refreshToken || localStorage.getItem('refresh_token');
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        });

        const { access_token, refresh_token: new_refresh_token } = response.data;

        // Update store
        useAuthStore.getState().setTokens(access_token, new_refresh_token);

        processQueue(null, access_token);

        // Retry original request
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
        }
        return api(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        // Only logout if refresh itself explicitly failed with 401
        // (not network errors or other issues)
        const refreshErr = refreshError as AxiosError;
        if (refreshErr.response?.status === 401) {
          useAuthStore.getState().logout();
          window.location.href = '/login';
        }
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    // Debug mode logging
    if (DEBUG_MODE && error.response) {
      console.error('[API] Request failed:', {
        url: originalRequest?.url,
        status: error.response.status,
        data: error.response.data,
      });
    }

    return Promise.reject(error);
  }
);

// Generic API methods
export const get = async <T>(url: string, params?: Record<string, unknown>): Promise<T> => {
  const response = await api.get<T>(url, { params });
  return response.data;
};

export const post = async <T>(url: string, data?: unknown): Promise<T> => {
  const response = await api.post<T>(url, data);
  return response.data;
};

export const patch = async <T>(url: string, data?: unknown): Promise<T> => {
  const response = await api.patch<T>(url, data);
  return response.data;
};

export const del = async <T>(url: string): Promise<T> => {
  const response = await api.delete<T>(url);
  return response.data;
};

export default api;
