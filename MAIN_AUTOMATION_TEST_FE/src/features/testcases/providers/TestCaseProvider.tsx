import { createContext, useCallback, useContext, useEffect, useState, type Dispatch, type ReactNode, type SetStateAction } from 'react';
import { message } from 'antd';
import { testcaseApi } from '../api/testcase-api';
import type { TestCasePayload } from '../types';

interface TestCaseContextValue {
  data: TestCasePayload | null;
  loading: boolean;
  saving: boolean;
  loadData: () => Promise<void>;
  saveData: (payload: TestCasePayload) => Promise<boolean>;
  setData: Dispatch<SetStateAction<TestCasePayload | null>>;
}

const TestCaseContext = createContext<TestCaseContextValue | null>(null);

export function TestCaseProvider({ children }: { children: ReactNode }) {
  const [data, setData] = useState<TestCasePayload | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      setData(await testcaseApi.getAll());
    } catch (e) {
      message.error(e instanceof Error ? e.message : 'Không tải được danh sách test case');
    } finally {
      setLoading(false);
    }
  }, []);

  const saveData = useCallback(async (payload: TestCasePayload) => {
    setSaving(true);
    try {
      const res = await testcaseApi.save(payload);
      setData(res.data);
      message.success(res.message || 'Đã lưu JSON');
      return true;
    } catch (e) {
      message.error(e instanceof Error ? e.message : 'Lưu thất bại');
      return false;
    } finally {
      setSaving(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  return (
    <TestCaseContext.Provider value={{ data, loading, saving, loadData, saveData, setData }}>
      {children}
    </TestCaseContext.Provider>
  );
}

export function useTestCases() {
  const ctx = useContext(TestCaseContext);
  if (!ctx) throw new Error('useTestCases must be used within TestCaseProvider');
  return ctx;
}
