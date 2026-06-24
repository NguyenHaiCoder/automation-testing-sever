import { Typography } from 'antd';
import type { TestResult } from '../types';

const { Text, Paragraph } = Typography;

const RESULT_STYLES: Record<string, { bg: string; color: string; border: string }> = {
  Pass: { bg: '#f6ffed', color: '#389e0d', border: '#b7eb8f' },
  Fail: { bg: '#fff2f0', color: '#cf1322', border: '#ffccc7' },
  Untested: { bg: '#fafafa', color: '#595959', border: '#d9d9d9' },
  'N/A': { bg: '#fafafa', color: '#8c8c8c', border: '#d9d9d9' },
};

export function ResultTag({ result }: { result: TestResult }) {
  const style = RESULT_STYLES[result] ?? RESULT_STYLES.Untested;
  return (
    <span
      style={{
        display: 'inline-block',
        minWidth: 72,
        textAlign: 'center',
        fontWeight: 600,
        padding: '2px 8px',
        borderRadius: 4,
        fontSize: 12,
        background: style.bg,
        color: style.color,
        border: `1px solid ${style.border}`,
      }}
    >
      {result || 'Untested'}
    </span>
  );
}

export function MultilineCell({ text }: { text: string }) {
  if (!text) return <Text type="secondary">—</Text>;
  return (
    <Paragraph style={{ margin: 0, whiteSpace: 'pre-wrap', fontSize: 13 }} ellipsis={{ rows: 3, expandable: true }}>
      {text}
    </Paragraph>
  );
}
