/**
 * Centralized configuration for CondoManager frontend
 * Handles environment-specific settings and feature flags
 */

// API Configuration
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
export const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';

// App Information
export const APP_NAME = import.meta.env.VITE_APP_NAME || 'CondoManager';
export const APP_SHORT_NAME = import.meta.env.VITE_APP_SHORT_NAME || 'Condo';
export const THEME_COLOR = import.meta.env.VITE_THEME_COLOR || '#0f172a';

// Environment Detection
export const IS_PRODUCTION = import.meta.env.PROD;
export const IS_DEVELOPMENT = import.meta.env.DEV;
export const IS_TEST = import.meta.env.MODE === 'test';
export const ENVIRONMENT = import.meta.env.MODE;

// Feature Flags
export const ENABLE_PUSH_NOTIFICATIONS = import.meta.env.VITE_ENABLE_PUSH_NOTIFICATIONS === 'true' || !IS_PRODUCTION;
export const ENABLE_SERVICE_WORKER = import.meta.env.VITE_ENABLE_SERVICE_WORKER === 'true' || !IS_PRODUCTION;
export const DEBUG_MODE = import.meta.env.VITE_DEBUG === 'true' || IS_DEVELOPMENT;
export const PWA_MODE = import.meta.env.VITE_PWA_MODE === 'true';

// Telegram Bot Configuration
export const TELEGRAM_BOT_USERNAME = import.meta.env.VITE_TELEGRAM_BOT_USERNAME || '';

// Error Tracking (Sentry)
export const SENTRY_DSN = import.meta.env.VITE_SENTRY_DSN || '';

/**
 * Configuration object for convenient access
 */
export const config = {
  apiUrl: API_BASE_URL,
  wsUrl: WS_BASE_URL,
  appName: APP_NAME,
  appShortName: APP_SHORT_NAME,
  themeColor: THEME_COLOR,
  environment: ENVIRONMENT,
  isProduction: IS_PRODUCTION,
  isDevelopment: IS_DEVELOPMENT,
  isTest: IS_TEST,
  features: {
    pushNotifications: ENABLE_PUSH_NOTIFICATIONS,
    serviceWorker: ENABLE_SERVICE_WORKER,
    debug: DEBUG_MODE,
    pwa: PWA_MODE,
  },
  telegram: {
    botUsername: TELEGRAM_BOT_USERNAME,
    botLink: TELEGRAM_BOT_USERNAME ? `https://t.me/${TELEGRAM_BOT_USERNAME}` : '',
  },
  sentry: {
    dsn: SENTRY_DSN,
    enabled: !!SENTRY_DSN && IS_PRODUCTION,
  },
} as const;

/**
 * Get API URL with path
 */
export function getApiUrl(path: string): string {
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${API_BASE_URL}${cleanPath}`;
}

/**
 * Get WebSocket URL with path
 */
export function getWsUrl(path: string): string {
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${WS_BASE_URL}${cleanPath}`;
}

/**
 * Log configuration in development mode
 */
if (IS_DEVELOPMENT) {
  console.log('[Config] Environment:', ENVIRONMENT);
  console.log('[Config] API URL:', API_BASE_URL);
  console.log('[Config] WS URL:', WS_BASE_URL);
  console.log('[Config] Features:', config.features);
}

export default config;
