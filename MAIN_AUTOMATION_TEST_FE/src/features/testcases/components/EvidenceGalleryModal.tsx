import { FileImageOutlined } from '@ant-design/icons';
import { Divider, Empty, Image, Modal, Space, Typography } from 'antd';
import { ResultTag } from '@/features/testcases';
import type { EvidenceRunGroup } from '../utils/evidence';

const { Text, Title } = Typography;

interface EvidenceGalleryModalProps {
  open: boolean;
  testCaseId: string;
  runs: EvidenceRunGroup[];
  onClose: () => void;
}

export function EvidenceGalleryModal({ open, testCaseId, runs, onClose }: EvidenceGalleryModalProps) {
  const totalImages = runs.reduce((sum, run) => sum + run.images.length, 0);

  return (
    <Modal
      title={
        <Space>
          <FileImageOutlined />
          <span>Minh chứng — {testCaseId}</span>
        </Space>
      }
      open={open}
      onCancel={onClose}
      footer={null}
      width={760}
      destroyOnClose
      className="evidence-gallery-modal"
    >
      {totalImages === 0 ? (
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description="Chưa có minh chứng cho test case này"
          style={{ padding: '32px 0' }}
        />
      ) : (
        <div className="evidence-gallery-runs">
          {runs.map((run, index) => (
            <section key={`${run.runNumber}-${run.testDate}`} className="evidence-run-section">
              {index > 0 && <Divider style={{ margin: '20px 0' }} />}
              <div className="evidence-run-header">
                <Title level={5} style={{ margin: 0 }}>
                  {run.title}
                </Title>
                <Space size="middle" wrap>
                  <ResultTag result={run.result} />
                  {run.testDate ? <Text type="secondary">Ngày test: {run.testDate}</Text> : null}
                  <Text type="secondary">{run.images.length} ảnh</Text>
                </Space>
              </div>
              <div className="evidence-gallery-grid">
                {run.images.map((img) => (
                  <div key={`${run.runNumber}-${img.url}-${img.name}`} className="evidence-gallery-item">
                    <Image
                      src={img.url}
                      alt={img.name}
                      className="evidence-gallery-image"
                      fallback="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='140'%3E%3Crect fill='%23f5f5f5' width='100%25' height='100%25'/%3E%3Ctext x='50%25' y='50%25' text-anchor='middle' dy='.3em' fill='%23999' font-size='12'%3EKhong tai duoc anh%3C/text%3E%3C/svg%3E"
                    />
                    <Text className="evidence-gallery-caption" ellipsis title={img.name}>
                      {img.name}
                    </Text>
                  </div>
                ))}
              </div>
            </section>
          ))}
        </div>
      )}
    </Modal>
  );
}
