import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  MinusCircleOutlined,
  PictureOutlined,
  PlayCircleOutlined,
  SearchOutlined,
} from '@ant-design/icons';
import { Badge, Button, Card, Col, Descriptions, Drawer, Input, Row, Select, Space, Statistic, Table, Typography } from 'antd';
import type { ColumnsType, TableRowSelection } from 'antd/es/table/interface';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { EvidenceGalleryModal } from '@/features/testcases/components/EvidenceGalleryModal';
import { MultilineCell, ResultTag, useTestCases, type TestCase, type TestResult } from '@/features/testcases';
import { countEvidenceImages, resolveEvidenceRuns } from '@/features/testcases/utils/evidence';
import { parseTestCaseGroup, TEST_CASE_GROUP_OPTIONS } from '@/features/testcases/utils/test-case-group';
import { useTablePagination } from '@/shared';

const { Text, Link } = Typography;

export interface DashboardPageProps {
  jobRunning?: boolean;
  onRunCases: (caseIds: string[]) => Promise<boolean>;
}

export function DashboardPage({ jobRunning = false, onRunCases }: DashboardPageProps) {
  const { data, loading } = useTestCases();
  const [search, setSearch] = useState('');
  const [resultFilter, setResultFilter] = useState('all');
  const [groupFilter, setGroupFilter] = useState<'all' | 'ADMIN' | 'OFFICER' | 'EMPLOYEE' | 'BR'>('all');
  const [sectionFilter, setSectionFilter] = useState('all');
  const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([]);
  const [detailCase, setDetailCase] = useState<TestCase | null>(null);
  const [evidenceCase, setEvidenceCase] = useState<TestCase | null>(null);
  const { resetPage, buildPagination } = useTablePagination({ defaultPageSize: 15, itemLabel: 'test case' });

  const runCases = useCallback(
    async (ids: string[]) => {
      const cleaned = [...new Set(ids.map((id) => String(id).trim()).filter(Boolean))];
      if (!cleaned.length) return;
      await onRunCases(cleaned);
    },
    [onRunCases],
  );

  const sections = useMemo(() => {
    if (!data) return [];
    const pool =
      groupFilter === 'all'
        ? data.cases
        : data.cases.filter((c) => parseTestCaseGroup(c) === groupFilter);
    return [...new Set(pool.map((c) => c.section).filter(Boolean))];
  }, [data, groupFilter]);

  const filteredCases = useMemo(() => {
    if (!data) return [];
    const q = search.trim().toLowerCase();
    return data.cases.filter((c) => {
      if (resultFilter !== 'all' && c.result !== resultFilter) return false;
      if (groupFilter !== 'all' && parseTestCaseGroup(c) !== groupFilter) return false;
      if (sectionFilter !== 'all' && c.section !== sectionFilter) return false;
      if (!q) return true;
      const hay = [c.id, c.description, c.procedure, c.note, c.section].join(' ').toLowerCase();
      return hay.includes(q);
    });
  }, [data, search, resultFilter, groupFilter, sectionFilter]);

  const filteredIds = useMemo(() => new Set(filteredCases.map((c) => c.id)), [filteredCases]);

  const rowSelection: TableRowSelection<TestCase> = {
    selectedRowKeys,
    onChange: (keys) => setSelectedRowKeys(keys as string[]),
    preserveSelectedRowKeys: true,
    fixed: true,
    columnWidth: 48,
    getCheckboxProps: () => ({ disabled: jobRunning }),
  };

  useEffect(() => {
    resetPage();
  }, [search, resultFilter, groupFilter, sectionFilter, resetPage]);

  useEffect(() => {
    if (sectionFilter !== 'all' && !sections.includes(sectionFilter)) {
      setSectionFilter('all');
    }
  }, [groupFilter, sectionFilter, sections]);

  const columns: ColumnsType<TestCase> = [
    {
      title: 'ID',
      dataIndex: 'id',
      width: 120,
      fixed: 'left',
      render: (id: string) => <Text strong style={{ color: '#cf1322' }}>{id}</Text>,
    },
    { title: 'Mô tả test case', dataIndex: 'description', width: 280, render: (v: string) => <MultilineCell text={v} /> },
    { title: 'Quy trình', dataIndex: 'procedure', width: 320, render: (v: string) => <MultilineCell text={v} /> },
    { title: 'Kết quả mong đợi', dataIndex: 'expected', width: 300, render: (v: string) => <MultilineCell text={v} /> },
    { title: 'Phụ thuộc', dataIndex: 'dependence', width: 220, render: (v: string) => <MultilineCell text={v} /> },
    { title: 'TestData', dataIndex: 'testData', width: 180, render: (v: string) => <MultilineCell text={v} /> },
    {
      title: 'Kết quả',
      dataIndex: 'result',
      width: 100,
      align: 'center',
      render: (r: TestResult) => <ResultTag result={r} />,
    },
    { title: 'Ngày test', dataIndex: 'testDate', width: 110 },
    {
      title: 'Ghi chú',
      dataIndex: 'note',
      width: 200,
      render: (v: string) =>
        v.startsWith('http') ? (
          <Link href={v} target="_blank" ellipsis>{v}</Link>
        ) : (
          <MultilineCell text={v} />
        ),
    },
    {
      title: 'Minh chứng',
      key: 'evidence',
      width: 120,
      align: 'center',
      render: (_, record) => {
        const count = countEvidenceImages(record);
        return (
          <Button
            type="link"
            size="small"
            icon={<PictureOutlined />}
            onClick={() => setEvidenceCase(record)}
          >
            Xem ảnh{count > 0 ? ` (${count})` : ''}
          </Button>
        );
      },
    },
    {
      title: 'Thao tác',
      key: 'action',
      width: 110,
      align: 'center',
      render: (_, record) => (
        <Button
          type="primary"
          size="small"
          icon={<PlayCircleOutlined />}
          disabled={jobRunning}
          onClick={() => void runCases([record.id])}
        >
          Bắt đầu
        </Button>
      ),
    },
  ];

  const stats = data?.stats;
  const selectedInView = selectedRowKeys.filter((id) => filteredIds.has(id));

  return (
    <>
      <Card className="meta-card" bordered={false}>
        <Descriptions column={{ xs: 1, sm: 2, lg: 3 }} size="small">
          <Descriptions.Item label="Mã module">{data?.moduleCode ?? '—'}</Descriptions.Item>
          <Descriptions.Item label="Yêu cầu kiểm thử">{data?.requirement ?? '—'}</Descriptions.Item>
          <Descriptions.Item label="Tester">{data?.tester ?? '—'}</Descriptions.Item>
        </Descriptions>
      </Card>

      <Row gutter={[12, 12]} className="stats-row">
        <Col xs={12} sm={8} md={4}>
          <Card className="stat-card stat-pass" bordered={false}>
            <Statistic title="Pass" value={stats?.pass ?? 0} prefix={<CheckCircleOutlined />} valueStyle={{ color: '#389e0d' }} />
          </Card>
        </Col>
        <Col xs={12} sm={8} md={4}>
          <Card className="stat-card stat-fail" bordered={false}>
            <Statistic title="Fail" value={stats?.fail ?? 0} prefix={<CloseCircleOutlined />} valueStyle={{ color: '#cf1322' }} />
          </Card>
        </Col>
        <Col xs={12} sm={8} md={4}>
          <Card className="stat-card stat-untested" bordered={false}>
            <Statistic title="Untested" value={stats?.untested ?? 0} valueStyle={{ color: '#595959' }} />
          </Card>
        </Col>
        <Col xs={12} sm={8} md={4}>
          <Card className="stat-card stat-na" bordered={false}>
            <Statistic title="N/A" value={stats?.na ?? 0} prefix={<MinusCircleOutlined />} valueStyle={{ color: '#8c8c8c' }} />
          </Card>
        </Col>
        <Col xs={24} sm={16} md={8}>
          <Card className="stat-card stat-total" bordered={false}>
            <Statistic title="Tổng test case" value={stats?.total ?? 0} />
            <div className="progress-bar">
              <div className="progress-pass" style={{ width: `${((stats?.pass ?? 0) / (stats?.total || 1)) * 100}%` }} />
              <div className="progress-fail" style={{ width: `${((stats?.fail ?? 0) / (stats?.total || 1)) * 100}%` }} />
            </div>
          </Card>
        </Col>
      </Row>

      <Card
        className="table-card"
        bordered={false}
        title={
          <Space wrap>
            <span>Danh sách test case</span>
            <Badge count={filteredCases.length} style={{ backgroundColor: '#1677ff' }} showZero overflowCount={999} />
            {selectedRowKeys.length > 0 && (
              <Badge count={selectedRowKeys.length} style={{ backgroundColor: '#52c41a' }} overflowCount={999} title="Đã chọn" />
            )}
          </Space>
        }
        extra={
          selectedRowKeys.length > 0 ? (
            <Space wrap>
              <Button size="small" onClick={() => setSelectedRowKeys([])} disabled={jobRunning}>
                Bỏ chọn
              </Button>
              <Button
                type="primary"
                size="small"
                icon={<PlayCircleOutlined />}
                disabled={jobRunning}
                onClick={() => void runCases(selectedRowKeys)}
              >
                Chạy đã chọn ({selectedRowKeys.length})
              </Button>
            </Space>
          ) : null
        }
      >
        <Space wrap style={{ marginBottom: 16, width: '100%' }}>
          <Input
            allowClear
            prefix={<SearchOutlined />}
            placeholder="Tìm theo ID, mô tả, ghi chú..."
            style={{ width: 320, maxWidth: '100%' }}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <Select
            value={resultFilter}
            onChange={setResultFilter}
            style={{ width: 140 }}
            options={[
              { value: 'all', label: 'Tất cả KQ' },
              { value: 'Pass', label: 'Pass' },
              { value: 'Fail', label: 'Fail' },
              { value: 'Untested', label: 'Untested' },
              { value: 'N/A', label: 'N/A' },
            ]}
          />
          <Select
            value={groupFilter}
            onChange={setGroupFilter}
            style={{ width: 180 }}
            options={TEST_CASE_GROUP_OPTIONS}
          />
          <Select
            value={sectionFilter}
            onChange={setSectionFilter}
            style={{ minWidth: 280 }}
            placeholder="Phân loại chi tiết"
            options={[{ value: 'all', label: 'Tất cả phân loại' }, ...sections.map((s) => ({ value: s, label: s }))]}
          />
          {selectedInView.length > 0 && (
            <Button
              type="primary"
              icon={<PlayCircleOutlined />}
              disabled={jobRunning}
              onClick={() => void runCases(selectedInView)}
            >
              Chạy {selectedInView.length} case trên trang
            </Button>
          )}
        </Space>

        <Table<TestCase>
          rowKey="id"
          loading={loading}
          columns={columns}
          dataSource={filteredCases}
          rowSelection={rowSelection}
          className="dashboard-testcase-table"
          scroll={{ x: 'max-content' }}
          pagination={buildPagination(filteredCases.length)}
          size="small"
          bordered
          onRow={(record) => ({ onDoubleClick: () => setDetailCase(record) })}
          rowClassName={(record) => {
            if (record.result === 'Pass') return 'row-pass';
            if (record.result === 'Fail') return 'row-fail';
            return '';
          }}
        />
        <Text type="secondary" style={{ fontSize: 12 }}>
          Tick chọn nhiều case · Bấm Bắt đầu hoặc Chạy đã chọn — cùng 1 Chromium, chạy lần lượt · Kéo ngang bảng để xem thêm cột.
        </Text>
      </Card>

      <Drawer title={detailCase ? `Chi tiết — ${detailCase.id}` : 'Chi tiết'} width={640} open={!!detailCase} onClose={() => setDetailCase(null)}>
        {detailCase && (
          <Descriptions column={1} bordered size="small">
            <Descriptions.Item label="Nhóm">{detailCase.section}</Descriptions.Item>
            <Descriptions.Item label="Mô tả">{detailCase.description}</Descriptions.Item>
            <Descriptions.Item label="Quy trình"><pre className="detail-pre">{detailCase.procedure}</pre></Descriptions.Item>
            <Descriptions.Item label="Kết quả mong đợi"><pre className="detail-pre">{detailCase.expected}</pre></Descriptions.Item>
            {detailCase.passCondition ? (
              <Descriptions.Item label="Điều kiện Pass"><pre className="detail-pre">{detailCase.passCondition}</pre></Descriptions.Item>
            ) : null}
            {detailCase.failCondition ? (
              <Descriptions.Item label="Điều kiện Fail"><pre className="detail-pre">{detailCase.failCondition}</pre></Descriptions.Item>
            ) : null}
            <Descriptions.Item label="Phụ thuộc">{detailCase.dependence || '—'}</Descriptions.Item>
            <Descriptions.Item label="TestData">{detailCase.testData || '—'}</Descriptions.Item>
            <Descriptions.Item label="Kết quả"><ResultTag result={detailCase.result} /></Descriptions.Item>
            <Descriptions.Item label="Ngày test">{detailCase.testDate || '—'}</Descriptions.Item>
            <Descriptions.Item label="Ghi chú">{detailCase.note || '—'}</Descriptions.Item>
            <Descriptions.Item label="Minh chứng">
              <Button type="link" size="small" icon={<PictureOutlined />} onClick={() => setEvidenceCase(detailCase)}>
                Xem ảnh ({countEvidenceImages(detailCase)})
              </Button>
            </Descriptions.Item>
            <Descriptions.Item label="Thao tác">
              <Button
                type="primary"
                size="small"
                icon={<PlayCircleOutlined />}
                disabled={jobRunning}
                onClick={() => runCases([detailCase.id])}
              >
                Bắt đầu
              </Button>
            </Descriptions.Item>
          </Descriptions>
        )}
      </Drawer>

      <EvidenceGalleryModal
        open={!!evidenceCase}
        testCaseId={evidenceCase?.id ?? ''}
        runs={evidenceCase ? resolveEvidenceRuns(evidenceCase) : []}
        onClose={() => setEvidenceCase(null)}
      />
    </>
  );
}
