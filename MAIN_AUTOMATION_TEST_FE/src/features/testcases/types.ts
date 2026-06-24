export type TestResult = 'Pass' | 'Fail' | 'Untested' | 'N/A' | (string & {});

/** Ref minh chứng — url trực tiếp hoặc runId + rel từ log API */
export interface EvidenceImageRef {
  url?: string;
  runId?: string;
  runType?: string;
  rel?: string;
  name?: string;
}

/** Một lần chạy test — nhóm ảnh minh chứng theo lần */
export interface EvidenceRun {
  runNumber: number;
  runId: string;
  runType?: string;
  testDate: string;
  result: TestResult;
  message?: string;
  images: EvidenceImageRef[];
}

export interface TestCase {
  id: string;
  section: string;
  description: string;
  procedure: string;
  expected: string;
  dependence: string;
  testData: string;
  result: TestResult;
  testDate: string;
  note: string;
  evidence: string;
  evidenceImages?: EvidenceImageRef[];
  evidenceRuns?: EvidenceRun[];
  passCondition?: string;
  failCondition?: string;
}

export interface TestStats {
  pass: number;
  fail: number;
  untested: number;
  na: number;
  total: number;
}

export interface TestCasePayload {
  moduleCode: string;
  requirement: string;
  tester: string;
  stats: TestStats;
  cases: TestCase[];
  exportedAt?: string;
  updatedAt?: string;
}

export interface SaveTestCaseResponse {
  ok: boolean;
  message: string;
  data: TestCasePayload;
}

export const EMPTY_TEST_CASE: TestCase = {
  id: '',
  section: '',
  description: '',
  procedure: '',
  expected: '',
  dependence: '',
  testData: '',
  result: 'Untested',
  testDate: '',
  note: '',
  evidence: '',
};

export const TEST_RESULT_OPTIONS = [
  { value: 'Untested', label: 'Untested' },
  { value: 'Pass', label: 'Pass' },
  { value: 'Fail', label: 'Fail' },
  { value: 'N/A', label: 'N/A' },
] as const;
