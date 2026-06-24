import { apiRequest } from '@/shared/api/http-client';
import type { SaveTestCaseResponse, TestCasePayload } from '../types';

export const testcaseApi = {
  getAll() {
    return apiRequest<TestCasePayload>('/testcases');
  },

  save(payload: TestCasePayload) {
    return apiRequest<SaveTestCaseResponse>('/testcases', {
      method: 'PUT',
      body: JSON.stringify(payload),
    });
  },
} as const;
