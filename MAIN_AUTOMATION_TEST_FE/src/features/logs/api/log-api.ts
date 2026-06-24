import { API_BASE_URL } from '@/shared/api/config';
import { apiRequest } from '@/shared/api/http-client';
import type { LogDetail, LogsListResponse } from '../types';

export function buildLogFileUrl(runId: string, rel: string): string {
  const q = new URLSearchParams({ runId, rel });
  return `${API_BASE_URL}/logs/file?${q.toString()}`;
}

export const logApi = {
  list() {
    return apiRequest<LogsListResponse>('/logs');
  },

  getDetail(runIdOrPath: string, byRunId = false) {
    const q = byRunId
      ? `runId=${encodeURIComponent(runIdOrPath)}`
      : `path=${encodeURIComponent(runIdOrPath)}`;
    return apiRequest<LogDetail>(`/logs/detail?${q}`);
  },

  fileUrl(runId: string, rel: string) {
    return buildLogFileUrl(runId, rel);
  },
} as const;
