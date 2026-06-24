import { FileImageOutlined, FileOutlined, FileTextOutlined } from '@ant-design/icons';
import { Card, Collapse, Image, Space, Tag, Typography } from 'antd';
import type { ReactNode } from 'react';
import { logApi, type LogFileEntry, type LogRoleBundle } from '@/features/logs';

const { Text } = Typography;

const ROLE_COLORS: Record<string, string> = {
  ADMIN: 'red',
  OFFICER: 'blue',
  EMPLOYEE: 'green',
  OTHER: 'default',
};

interface LogRolePanelProps {
  bundle: LogRoleBundle;
  runId: string;
}

function FileRow({ file, runId }: { file: LogFileEntry; runId: string }) {
  const isImage = file.kind === 'image';
  const url = logApi.fileUrl(runId, file.rel);

  return (
    <div className={`log-file-item${isImage ? ' log-file-image' : ''}`}>
      <Space size={8}>
        {isImage ? (
          <Image
            src={url}
            alt={file.name}
            width={36}
            height={36}
            style={{ objectFit: 'cover', borderRadius: 4, cursor: 'zoom-in' }}
            preview={{ mask: 'Xem' }}
          />
        ) : (
          <FileOutlined />
        )}
        <Text style={{ fontSize: 12 }}>{file.name}</Text>
      </Space>
      <Text type="secondary" style={{ fontSize: 11 }}>{(file.size / 1024).toFixed(1)} KB</Text>
    </div>
  );
}

export function LogRolePanel({ bundle, runId }: LogRolePanelProps) {
  const role = bundle.role;
  const pictureUrls = bundle.pictures.map((p) => logApi.fileUrl(runId, p.rel));

  const items = [
    bundle.pictures.length > 0 && {
      key: 'pictures',
      label: (
        <Space>
          <FileImageOutlined />
          Ảnh ({bundle.pictures.length})
        </Space>
      ),
      children: (
        <>
          <Image.PreviewGroup items={pictureUrls}>
            <div className="log-image-grid">
              {bundle.pictures.map((pic) => (
                <div key={pic.rel} className="log-image-thumb">
                  <Image
                    src={logApi.fileUrl(runId, pic.rel)}
                    alt={pic.name}
                    width={120}
                    height={80}
                    style={{ objectFit: 'cover', borderRadius: 6 }}
                    fallback="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='80'%3E%3Crect fill='%23f0f0f0' width='100%25' height='100%25'/%3E%3Ctext x='50%25' y='50%25' text-anchor='middle' dy='.3em' fill='%23999' font-size='12'%3ELoi anh%3C/text%3E%3C/svg%3E"
                  />
                  <Text className="log-image-name" ellipsis title={pic.name}>
                    {pic.name.split('/').pop()}
                  </Text>
                </div>
              ))}
            </div>
          </Image.PreviewGroup>
          <div className="log-file-list" style={{ marginTop: 12 }}>
            {bundle.pictures.map((f) => (
              <FileRow key={f.rel} file={f} runId={runId} />
            ))}
          </div>
        </>
      ),
    },
    bundle.jsonFiles.length > 0 && {
      key: 'json',
      label: `JSON (${bundle.jsonFiles.length})`,
      children: (
        <div className="log-file-list">
          {bundle.jsonFiles.map((f) => (
            <FileRow key={f.rel} file={f} runId={runId} />
          ))}
        </div>
      ),
    },
    bundle.logTail && {
      key: 'log',
      label: (
        <Space>
          <FileTextOutlined />
          Log theo role
        </Space>
      ),
      children: <pre className="log-pre">{bundle.logTail}</pre>,
    },
    bundle.others.length > 0 && {
      key: 'others',
      label: `File khác (${bundle.others.length})`,
      children: (
        <div className="log-file-list">
          {bundle.others.map((f) => (
            <FileRow key={f.rel} file={f} runId={runId} />
          ))}
        </div>
      ),
    },
  ].filter(Boolean) as { key: string; label: ReactNode; children: ReactNode }[];

  if (!items.length) return null;

  return (
    <Card
      size="small"
      className="log-role-card"
      title={
        <Tag color={ROLE_COLORS[role] ?? 'default'} style={{ fontWeight: 600, fontSize: 13 }}>
          {role}
        </Tag>
      }
      style={{ marginBottom: 12 }}
    >
      <Collapse size="small" defaultActiveKey={['pictures']} items={items} />
    </Card>
  );
}
