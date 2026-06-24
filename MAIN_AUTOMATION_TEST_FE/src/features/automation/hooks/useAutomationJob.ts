import { useCallback, useEffect, useRef, useState } from 'react';
import { message } from 'antd';
import { automationApi } from '../api/automation-api';

interface UseAutomationJobOptions {
  onJobFinished?: () => void;
  pollIntervalMs?: number;
}

export function useAutomationJob({ onJobFinished, pollIntervalMs = 2000 }: UseAutomationJobOptions = {}) {
  const [jobRunning, setJobRunning] = useState(false);
  const [jobMessage, setJobMessage] = useState('');
  const [runningCaseIds, setRunningCaseIds] = useState<string[]>([]);
  const [visibleBrowser, setVisibleBrowser] = useState(true);
  const jobRunningRef = useRef(false);
  const onJobFinishedRef = useRef(onJobFinished);

  useEffect(() => {
    onJobFinishedRef.current = onJobFinished;
  }, [onJobFinished]);

  useEffect(() => {
    jobRunningRef.current = jobRunning;
  }, [jobRunning]);

  const pollStatus = useCallback(async () => {
    try {
      const status = await automationApi.getStatus();
      const wasRunning = jobRunningRef.current;
      const running = status.job.running;
      setJobRunning(running);
      setJobMessage(status.job.message);
      jobRunningRef.current = running;
      if (wasRunning && !running) {
        setRunningCaseIds([]);
        onJobFinishedRef.current?.();
      }
      return running;
    } catch {
      return jobRunningRef.current;
    }
  }, []);

  useEffect(() => {
    void pollStatus();
    const id = window.setInterval(() => {
      void pollStatus();
    }, pollIntervalMs);
    return () => window.clearInterval(id);
  }, [pollStatus, pollIntervalMs]);

  const startExplore = useCallback(async () => {
    try {
      const res = await automationApi.startExplore(visibleBrowser);
      message.success(res.message);
      setJobRunning(true);
      jobRunningRef.current = true;
      void pollStatus();
    } catch (e) {
      message.error(e instanceof Error ? e.message : 'Không khởi chạy được Khám phá');
    }
  }, [pollStatus, visibleBrowser]);

  const startRun = useCallback(async () => {
    try {
      const res = await automationApi.startRun(visibleBrowser);
      message.success(res.message);
      setJobRunning(true);
      jobRunningRef.current = true;
      void pollStatus();
    } catch (e) {
      message.error(e instanceof Error ? e.message : 'Không khởi chạy được kiểm thử');
    }
  }, [pollStatus, visibleBrowser]);

  const startCases = useCallback(async (caseIds: string[]) => {
    const ids = [...new Set(caseIds.map((id) => String(id).trim()).filter(Boolean))];
    if (!ids.length) {
      message.warning('Chọn ít nhất một test case');
      return false;
    }

    const hide = message.loading(`Đang khởi chạy ${ids.length} test case…`, 0);
    try {
      const res = await automationApi.startCases(ids, visibleBrowser);
      hide();
      message.success(res.message);
      setRunningCaseIds(ids);
      setJobRunning(true);
      jobRunningRef.current = true;
      setJobMessage(res.message);
      void pollStatus();
      return true;
    } catch (e) {
      hide();
      message.error(e instanceof Error ? e.message : 'Không khởi chạy được test case');
      return false;
    }
  }, [pollStatus, visibleBrowser]);

  const terminateJob = async () => {
    try {
      const res = await automationApi.stopJob();
      message.success(res.message);
      setJobRunning(false);
      jobRunningRef.current = false;
      setRunningCaseIds([]);
      setJobMessage(res.message);
      onJobFinishedRef.current?.();
    } catch (e) {
      message.error(e instanceof Error ? e.message : 'Không chấm dứt được tiến trình');
      await pollStatus();
    }
  };

  return {
    jobRunning,
    jobMessage,
    runningCaseIds,
    visibleBrowser,
    setVisibleBrowser,
    startExplore,
    startRun,
    startCases,
    terminateJob,
    pollStatus,
  };
}
