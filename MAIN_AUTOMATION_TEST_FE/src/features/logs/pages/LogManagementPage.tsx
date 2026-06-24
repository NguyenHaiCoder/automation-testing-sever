import { EyeOutlined, FolderOpenOutlined, ReloadOutlined } from '@ant-design/icons';
import { Button, Card, Descriptions, Drawer, Space, Table, Tabs, Tag, Typography } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useCallback, useEffect, useState } from 'react';
import { LogRolePanel, logApi, type LogDetail, type LogRun } from '@/features/logs';
import { useTablePagination } from '@/shared';

const { Text, Paragraph } = Typography;

const ROLE_ORDER = ['ADMIN', 'OFFICER', 'EMPLOYEE', 'OTHER'] as const;

export function LogManagementPage() {
  const [runs, setRuns] = useState<LogRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [detail, setDetail] = useState<LogDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [activeRoleTab, setActiveRoleTab] = useState('ADMIN');
  const { buildPagination } = useTablePagination({ defaultPageSize: 10, itemLabel: 'lần chạy' });

  const loadLogs = useCallback(async () => {
    setLoading(true);
    try {
      const res = await logApi.list();
      setRuns(res.runs);
    } catch {
      setRuns([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadLogs();
  }, [loadLogs]);

  const openDetail = async (run: LogRun) => {
    setDetailLoading(true);
    setDetail(null);
    try {
      const d = await logApi.getDetail(run.id, true);
      setDetail(d);
      const firstRole = d.roles.find((r) => ROLE_ORDER.includes(r.role as (typeof ROLE_ORDER)[number]))?.role ?? 'ADMIN';
      setActiveRoleTab(firstRole);
    } catch {
      setDetail({ ...run, summary: '', logTail: '', logByRole: {}, roles: [], files: [] });
    } finally {
      setDetailLoading(false);
    }
  };

  const columns: ColumnsType<LogRun> = [
    {
      title: 'Loại',
      dataIndex: 'type',
      width: 100,
      render: (t: string) => (
        <Tag color={t === 'explore' ? 'blue' : 'purple'}>{t === 'explore' ? 'Khám phá' : 'E2E Test'}</Tag>
      ),
    },
    { title: 'Run ID', dataIndex: 'id', width: 200, render: (v) => <Text code>{v}</Text> },
    { title: 'Thời gian', dataIndex: 'createdAt', width: 180 },
    {
      title: 'Ảnh theo role',
      width: 200,
      render: (_, r) => {
        const byRole = r.picturesByRole;
        if (!byRole || !Object.keys(byRole).length) {
          return <Text type="secondary">{r.pictureCount ?? 0} ảnh</Text>;
        }
        return (
          <Space size={4} wrap>
            {(['ADMIN', 'OFFICER', 'EMPLOYEE'] as const).map((role) =>
              byRole[role] ? (
                <Tag key={role} color={role === 'ADMIN' ? 'red' : role === 'OFFICER' ? 'blue' : 'green'}>
                  {role}: {byRole[role]}
                </Tag>
              ) : null,
            )}
          </Space>
        );
      },
    },
    {
      title: '',
      width: 80,
      render: (_, record) => (
        <Button type="link" icon={<EyeOutlined />} onClick={() => void openDetail(record)}>
          Xem
        </Button>
      ),
    },
  ];

  const roleTabs = detail?.roles
    .slice()
    .sort((a, b) => ROLE_ORDER.indexOf(a.role as (typeof ROLE_ORDER)[number]) - ROLE_ORDER.indexOf(b.role as (typeof ROLE_ORDER)[number]))
    .map((bundle) => ({
      key: bundle.role,
      label: (
        <span>
          {bundle.role}{' '}
          <Text type="secondary" style={{ fontSize: 11 }}>
            ({bundle.pictures.length} ảnh)
          </Text>
        </span>
      ),
      children: <LogRolePanel bundle={bundle} runId={detail.id} />,
    }));

  return (
    <>
      <Card
        bordered={false}
        className="table-card"
        title={
          <Space>
            <FolderOpenOutlined />
            Quản lý log automation
          </Space>
        }
        extra={
          <Button icon={<ReloadOutlined />} onClick={() => void loadLogs()} loading={loading}>
            Làm mới
          </Button>
        }
      >
        <Text type="secondary" style={{ display: 'block', marginBottom: 16 }}>
          Log khám phá: <code>MAIN_AUTOMATION_TEST/log/</code> · Ảnh theo role: <code>picture/ADMIN|OFFICER|EMPLOYEE/</code>
        </Text>

        <Table<LogRun>
          rowKey="path"
          loading={loading}
          columns={columns}
          dataSource={runs}
          pagination={buildPagination(runs.length)}
          size="small"
          bordered
        />
      </Card>

      <Drawer
        title={detail ? `Log — ${detail.id}` : 'Chi tiết log'}
        width={920}
        open={!!detail || detailLoading}
        onClose={() => setDetail(null)}
      >
        {detailLoading && !detail ? (
          <div style={{ textAlign: 'center', padding: 48 }}>Đang tải...</div>
        ) : null}
        {detail && (
          <>
            <Descriptions column={1} bordered size="small" style={{ marginBottom: 16 }}>
              <Descriptions.Item label="Loại">
                <Tag color={detail.type === 'explore' ? 'blue' : 'purple'}>
                  {detail.type === 'explore' ? 'Khám phá UI' : 'E2E Test'}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Run ID">
                <Text code copyable>{detail.id}</Text>
              </Descriptions.Item>
              <Descriptions.Item label="Thời gian">{detail.createdAt}</Descriptions.Item>
            </Descriptions>

            {detail.summary && (
              <Card size="small" title="Summary" style={{ marginBottom: 12 }}>
                <Paragraph style={{ whiteSpace: 'pre-wrap', fontSize: 12, margin: 0 }}>{detail.summary}</Paragraph>
              </Card>
            )}

            {roleTabs && roleTabs.length > 0 ? (
              <Tabs activeKey={activeRoleTab} onChange={setActiveRoleTab} items={roleTabs} />
            ) : (
              <Card size="small" title="Log (tail)">
                <pre className="log-pre">{detail.logTail}</pre>
              </Card>
            )}
          </>
        )}
      </Drawer>
    </>
  );
}
