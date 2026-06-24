export type LogRunType = 'explore' | 'e2e';
export type LogRole = 'ADMIN' | 'OFFICER' | 'EMPLOYEE' | 'OTHER';
export type LogFileKind = 'image' | 'json' | 'log' | 'text' | 'other';

export interface LogRun {
  id: string;
  type: LogRunType;
  path: string;
  createdAt: string;
  mtime: number;
  summaryFile?: string;
  logFile?: string;
  jsonCount?: number;
  pictureCount?: number;
  picturesByRole?: Partial<Record<'ADMIN' | 'OFFICER' | 'EMPLOYEE', number>>;
  resultsFile?: string;
}

export interface LogFileEntry {
  name: string;
  rel: string;
  size: number;
  role?: LogRole | string | null;
  kind: LogFileKind | string;
  runId: string;
}

export interface LogRoleBundle {
  role: LogRole | string;
  pictures: LogFileEntry[];
  jsonFiles: LogFileEntry[];
  others: LogFileEntry[];
  logTail: string;
}

export interface LogDetail extends LogRun {
  summary: string;
  logTail: string;
  logByRole: Record<string, string>;
  roles: LogRoleBundle[];
  files: LogFileEntry[];
}

export interface LogsListResponse {
  runs: LogRun[];
  total: number;
}
