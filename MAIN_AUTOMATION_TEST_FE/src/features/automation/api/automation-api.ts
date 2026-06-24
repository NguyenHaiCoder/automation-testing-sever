import { apiRequest } from '@/shared/api/http-client';
import type { AutomationStatus, StartJobResponse } from '../types';

export const automationApi = {
  getStatus() {
    return apiRequest<AutomationStatus>('/status');
  },

  startExplore(visible = true) {
    return apiRequest<StartJobResponse>('/explore', {
      method: 'POST',
      body: JSON.stringify({ visible }),
    });
  },

  startRun(visible = true) {
    return apiRequest<StartJobResponse>('/run', {
      method: 'POST',
      body: JSON.stringify({ visible }),
    });
  },

  startCases(caseIds: string[], visible = true) {
    return apiRequest<StartJobResponse>('/run-cases', {
      method: 'POST',
      body: JSON.stringify({ caseIds, visible }),
    });
  },

  stopJob() {
    return apiRequest<StartJobResponse>('/stop', { method: 'POST' });
  },
} as const;
