export type JobMode = 'explore' | 'run' | 'cases';

export interface JobState {
  running: boolean;
  mode: JobMode | null;
  caseIds?: string[];
  startedAt: string | null;
  finishedAt: string | null;
  pid: number | null;
  exitCode: number | null;
  message: string;
}

export interface LastRunInfo {
  runDir: string;
  summary?: string;
  passed?: number;
  failed?: number;
  total?: number;
}

export interface AutomationStatus {
  job: JobState;
  lastExplore: LastRunInfo | null;
  lastE2E: LastRunInfo | null;
}

export interface StartJobResponse {
  ok: boolean;
  message: string;
  pid?: number;
  caseIds?: string[];
}
