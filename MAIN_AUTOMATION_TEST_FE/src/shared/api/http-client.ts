import { API_BASE_URL } from './config';

export class ApiError extends Error {
  readonly status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

export async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...init?.headers },
    ...init,
  });

  const data: unknown = await res.json();

  if (!res.ok) {
    const message =
      typeof data === 'object' && data !== null && 'error' in data
        ? String((data as { error: string }).error)
        : `HTTP ${res.status}`;
    throw new ApiError(message, res.status);
  }

  return data as T;
}
