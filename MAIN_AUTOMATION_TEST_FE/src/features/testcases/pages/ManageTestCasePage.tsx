import { DeleteOutlined, EditOutlined, PlusOutlined, SaveOutlined } from '@ant-design/icons';
import { Button, Card, Form, Input, Modal, Popconfirm, Select, Space, Table, Tag, Typography, message } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useEffect, useMemo, useState } from 'react';
import {
  EMPTY_TEST_CASE,
  ResultTag,
  TEST_RESULT_OPTIONS,
  useTestCases,
  type TestCase,
  type TestCasePayload,
} from '@/features/testcases';
import { useTablePagination } from '@/shared';

const { Text } = Typography;
const { TextArea } = Input;

export function ManageTestCasePage() {
  const { data, loading, saving, saveData, setData } = useTestCases();
  const [draft, setDraft] = useState<TestCasePayload | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<TestCase | null>(null);
  const [form] = Form.useForm<TestCase>();
  const [dirty, setDirty] = useState(false);
  const { buildPagination } = useTablePagination({ defaultPageSize: 15, itemLabel: 'test case' });

  useEffect(() => {
    if (data) setDraft(structuredClone(data));
  }, [data]);

  const sections = useMemo(() => {
    if (!draft) return [];
    return [...new Set(draft.cases.map((c) => c.section).filter(Boolean))];
  }, [draft]);

  const openCreate = () => {
    setEditing(null);
    form.setFieldsValue({ ...EMPTY_TEST_CASE, section: sections[0] ?? '' });
    setModalOpen(true);
  };

  const openEdit = (record: TestCase) => {
    setEditing(record);
    form.setFieldsValue(record);
    setModalOpen(true);
  };

  const handleModalOk = async () => {
    const values = await form.validateFields();
    if (!draft) return;

    const next = structuredClone(draft);
    if (editing) {
      const idx = next.cases.findIndex((c) => c.id === editing.id);
      if (idx >= 0) next.cases[idx] = values;
    } else {
      if (next.cases.some((c) => c.id === values.id)) {
        message.error('ID đã tồn tại');
        return;
      }
      next.cases.push(values);
    }
    setDraft(next);
    setData(next);
    setDirty(true);
    setModalOpen(false);
    message.success(editing ? 'Đã cập nhật (chưa lưu file)' : 'Đã thêm (chưa lưu file)');
  };

  const handleDelete = (id: string) => {
    if (!draft) return;
    const next = { ...draft, cases: draft.cases.filter((c) => c.id !== id) };
    setDraft(next);
    setData(next);
    setDirty(true);
    message.success('Đã xóa (chưa lưu file)');
  };

  const handleSaveJson = async () => {
    if (!draft) return;
    const ok = await saveData(draft);
    if (ok) setDirty(false);
  };

  const columns: ColumnsType<TestCase> = [
    { title: 'ID', dataIndex: 'id', width: 120, render: (v) => <Text strong style={{ color: '#cf1322' }}>{v}</Text> },
    { title: 'Nhóm', dataIndex: 'section', width: 200, ellipsis: true },
    { title: 'Mô tả', dataIndex: 'description', ellipsis: true },
    { title: 'Kết quả', dataIndex: 'result', width: 100, render: (r) => <ResultTag result={r} /> },
    {
      title: 'Thao tác',
      width: 120,
      fixed: 'right',
      render: (_, record) => (
        <Space>
          <Button type="text" icon={<EditOutlined />} onClick={() => openEdit(record)} />
          <Popconfirm title="Xóa test case này?" onConfirm={() => handleDelete(record.id)}>
            <Button type="text" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <Card
      bordered={false}
      className="table-card"
      title="Quản lý test case"
      extra={
        <Space wrap>
          {dirty && <Tag color="orange">Chưa lưu JSON</Tag>}
          <Button type="primary" icon={<SaveOutlined />} onClick={() => void handleSaveJson()} loading={saving} disabled={!dirty}>
            Lưu JSON
          </Button>
          <Button icon={<PlusOutlined />} onClick={openCreate}>
            Thêm mới
          </Button>
        </Space>
      }
    >
      <Text type="secondary" style={{ display: 'block', marginBottom: 16 }}>
        Chỉnh sửa test case rồi bấm <strong>Lưu JSON</strong> — dữ liệu lưu tại{' '}
        <code>MAIN_AUTOMATION_TEST/data/testcases.json</code>
      </Text>

      <Table<TestCase>
        rowKey="id"
        loading={loading}
        columns={columns}
        dataSource={draft?.cases ?? []}
        pagination={buildPagination(draft?.cases.length ?? 0)}
        size="small"
        bordered
        scroll={{ x: 900 }}
      />

      <Modal
        title={editing ? `Sửa — ${editing.id}` : 'Thêm test case mới'}
        open={modalOpen}
        onOk={() => void handleModalOk()}
        onCancel={() => setModalOpen(false)}
        width={720}
        destroyOnHidden
      >
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item name="id" label="ID" rules={[{ required: true, message: 'Nhập ID' }]}>
            <Input disabled={!!editing} placeholder="CL-List-99" />
          </Form.Item>
          <Form.Item name="section" label="Nhóm / Section" rules={[{ required: true }]}>
            <Input placeholder="Danh sách checklist — /hrm/checklist" list="section-list" />
            <datalist id="section-list">
              {sections.map((s) => (
                <option key={s} value={s} />
              ))}
            </datalist>
          </Form.Item>
          <Form.Item name="description" label="Mô tả" rules={[{ required: true }]}>
            <TextArea rows={2} />
          </Form.Item>
          <Form.Item name="procedure" label="Quy trình">
            <TextArea rows={3} />
          </Form.Item>
          <Form.Item name="expected" label="Kết quả mong đợi">
            <TextArea rows={3} />
          </Form.Item>
          <Form.Item name="dependence" label="Phụ thuộc">
            <TextArea rows={2} />
          </Form.Item>
          <Form.Item name="testData" label="TestData">
            <Input />
          </Form.Item>
          <Space style={{ width: '100%' }} size="middle">
            <Form.Item name="result" label="Kết quả" style={{ width: 160 }}>
              <Select options={[...TEST_RESULT_OPTIONS]} />
            </Form.Item>
            <Form.Item name="testDate" label="Ngày test" style={{ flex: 1 }}>
              <Input placeholder="2026-06-23" />
            </Form.Item>
          </Space>
          <Form.Item name="note" label="Ghi chú">
            <TextArea rows={2} />
          </Form.Item>
          <Form.Item name="evidence" label="Evidence">
            <Input />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
}
