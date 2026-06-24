/** API base — desktop Electron always hits local backend exe. */
const DESKTOP_API = 'http://127.0.0.1:8765/api';

function resolveApiBase(): string {
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL as string;
  }
  if (typeof window !== 'undefined' && window.location.protocol === 'file:') {
    return DESKTOP_API;
  }
  return '/api';
}

export const API_BASE_URL = resolveApiBase();
