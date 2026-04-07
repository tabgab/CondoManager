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
// Request interceptor to attach access token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token');
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
    const originalRequest = error.config;
    
    // Handle specific error codes
    if (error.response?.status === 401 && originalRequest && !(originalRequest as any)._retry) {
      (originalRequest as any)._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
          throw new Error('No refresh token');
        }
        
        // Try to refresh token
        const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        });
        
        const { access_token, refresh_token } = response.data;
        
        // Update store and localStorage
        useAuthStore.getState().setTokens(access_token, refresh_token);
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);
        
        // Retry original request with new token
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
        }
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed, logout user
        useAuthStore.getState().logout();
        if (!IS_PRODUCTION) {
          console.error('[API] Token refresh failed, redirecting to login');
        }
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    // Production error logging
    if (IS_PRODUCTION && error.response && error.response.status >= 500) {
      console.error('[API] Server Error:', error.response.status, error.message);
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
