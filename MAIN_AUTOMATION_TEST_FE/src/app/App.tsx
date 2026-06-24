import {
  CompassOutlined,
  FileSearchOutlined,
  PlayCircleOutlined,
  ReloadOutlined,
  StopOutlined,
} from '@ant-design/icons';
import { Alert, Button, Layout, Select, Space, Spin, Tooltip, Typography } from 'antd';
import { useCallback, useEffect, useState } from 'react';
import { useAutomationJob } from '@/features/automation';
import { DashboardPage } from '@/features/dashboard';
import { logApi, LogManagementPage } from '@/features/logs';
import { ManageTestCasePage, TestCaseProvider, useTestCases } from '@/features/testcases';
import { APP_VIEW_LABELS, AppSidebar, ADMIN_CONTACT_MESSAGE, RESTRICT_ADMIN, type AppView } from '@/shared';
import './App.css';

const { Header, Content } = Layout;
const { Title, Text } = Typography;

function AppShell() {
  const { data, loading, loadData } = useTestCases();
  const [collapsed, setCollapsed] = useState(false);
  const [activeView, setActiveView] = useState<AppView>('dashboard');
  const [logCount, setLogCount] = useState(0);

  const refreshLogCount = useCallback(async () => {
    if (RESTRICT_ADMIN) {
      setLogCount(0);
      return;
    }
    try {
      const res = await logApi.list();
      setLogCount(res.total);
    } catch {
      setLogCount(0);
    }
  }, []);

  const onJobFinished = useCallback(() => {
    void loadData();
    void refreshLogCount();
  }, [loadData, refreshLogCount]);

  const {
    jobRunning,
    jobMessage,
    runningCaseIds,
    visibleBrowser,
    setVisibleBrowser,
    startExplore,
    startRun,
    startCases,
    terminateJob,
  } = useAutomationJob({ onJobFinished });

  useEffect(() => {
    void refreshLogCount();
  }, [refreshLogCount]);

  const onNavigate = useCallback((view: AppView) => {
    if (RESTRICT_ADMIN && (view === 'manage' || view === 'logs')) return;
    setActiveView(view);
  }, []);

  useEffect(() => {
    if (RESTRICT_ADMIN && (activeView === 'manage' || activeView === 'logs')) {
      setActiveView('dashboard');
    }
  }, [activeView]);

  return (
    <Layout className="app-layout-root">
      <AppSidebar
        collapsed={collapsed}
        activeView={activeView}
        onCollapse={setCollapsed}
        onNavigate={onNavigate}
        caseCount={data?.cases.length ?? 0}
        logCount={logCount}
      />

      <Layout className="app-main">
        <Header className="app-header">
          <div className="header-inner">
            <Space align="center" size="middle">
              <FileSearchOutlined style={{ fontSize: 24, color: '#fff' }} />
              <div>
                <Title level={4} style={{ color: '#fff', margin: 0 }}>
                  Checklist Nhân sự — {APP_VIEW_LABELS[activeView]}
                </Title>
                <Text style={{ color: 'rgba(255,255,255,0.75)', fontSize: 13 }}>
                  H2Q Solution Tester · Playwright Automation
                </Text>
              </div>
            </Space>
            <Space wrap>
              <Tooltip title="Hiển thị cửa sổ Chromium khi chạy">
                <Select
                  value={visibleBrowser ? 'visible' : 'headless'}
                  onChange={(v) => setVisibleBrowser(v === 'visible')}
                  style={{ width: 150 }}
                  options={[
                    { value: 'visible', label: 'Chromium hiện' },
                    { value: 'headless', label: 'Headless' },
                  ]}
                />
              </Tooltip>
              <Button
                icon={<CompassOutlined />}
                size="large"
                className="btn-explore"
                disabled={jobRunning}
                onClick={() => void startExplore()}
              >
                Khám phá
              </Button>
              <Button
                type="primary"
                icon={<PlayCircleOutlined />}
                size="large"
                disabled={jobRunning}
                onClick={() => void startRun()}
              >
                Bắt đầu
              </Button>
              {jobRunning && (
                <Button
                  danger
                  type="primary"
                  icon={<StopOutlined />}
                  size="large"
                  className="btn-terminate"
                  onClick={() => void terminateJob()}
                >
                  Chấm dứt
                </Button>
              )}
              <Tooltip title="Tải lại từ testcases.json (không import Excel)">
                <Button icon={<ReloadOutlined />} size="large" onClick={() => void loadData()} disabled={loading}>
                  Làm mới
                </Button>
              </Tooltip>
            </Space>
          </div>
        </Header>

        <Content className="app-content">
          {jobRunning ? (
            <Alert
              type="info"
              showIcon
              icon={<Spin size="small" />}
              message="Đang chạy tự động..."
              description={
                runningCaseIds.length
                  ? `${jobMessage || 'Playwright đang thực thi'} — ${runningCaseIds.join(', ')}`
                  : jobMessage || 'Playwright đang thực thi — vui lòng chờ hoàn tất.'
              }
              style={{ marginBottom: 16 }}
            />
          ) : jobMessage && !jobMessage.startsWith('Dang chay') ? (
            <Alert
              type="success"
              showIcon
              message={jobMessage}
              closable
              style={{ marginBottom: 16 }}
            />
          ) : null}

          {activeView === 'dashboard' && (
            <DashboardPage jobRunning={jobRunning} onRunCases={startCases} />
          )}
          {activeView === 'manage' && !RESTRICT_ADMIN && <ManageTestCasePage />}
          {activeView === 'logs' && !RESTRICT_ADMIN && <LogManagementPage />}
          {RESTRICT_ADMIN && (activeView === 'manage' || activeView === 'logs') && (
            <Alert type="warning" showIcon message={ADMIN_CONTACT_MESSAGE} />
          )}
        </Content>
      </Layout>
    </Layout>
  );
}

export default function App() {
  return (
    <TestCaseProvider>
      <AppShell />
    </TestCaseProvider>
  );
}
