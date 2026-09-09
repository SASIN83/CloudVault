import axios from 'axios';

/**
 * Base URL resolution order:
 *  1. VITE_API_URL from .env (e.g. http://localhost:8000 or https://api.cloudvault.com)
 *  2. Fallback: same hostname that served the frontend + port 8000 (LAN/mobile friendly)
 *
 * If the configured URL points at localhost/127.0.0.1 but the app is opened
 * from another device (phone on LAN), the hostname is swapped to the real
 * host so mobile testing keeps working.
 *
 * NOTE: Vite reads .env only at startup — restart `npm run dev` after edits.
 */
const rawUrl =
  import.meta.env.VITE_API_URL || `http://${window.location.hostname}:8000`;

let baseURL = rawUrl;
try {
  const u = new URL(rawUrl);
  if (u.hostname === 'localhost' || u.hostname === '127.0.0.1') {
    u.hostname = window.location.hostname;   // LAN/phone fix
  }
  baseURL = u.toString().replace(/\/+$/, ''); // strip trailing slashes
} catch {
  // .env contains an invalid URL — keep the raw string and let axios complain loudly
}

console.info('[api] baseURL =', baseURL);   // ← verification line, remove once confirmed

const api = axios.create({ baseURL });

// Attach JWT to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Global 401 handling → back to login (skip on the login call itself)
api.interceptors.response.use(
  (res) => res,
  (err) => {
    const isLogin = err.config?.url?.includes('/auth/login');
    if (err.response?.status === 401 && !isLogin) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    if (err.response?.status === 429) {
      err.message = err.response?.data?.error || 'Too many requests — please slow down';
    }
    return Promise.reject(err);
  }
);

export default api;