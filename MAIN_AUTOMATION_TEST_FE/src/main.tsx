import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { ConfigProvider } from 'antd';
import viVN from 'antd/locale/vi_VN';
import App from '@/app/App';
import '@/index.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ConfigProvider
      locale={viVN}
      theme={{
        token: {
          colorPrimary: '#1677ff',
          borderRadius: 8,
          fontFamily: "'Segoe UI', system-ui, -apple-system, sans-serif",
        },
      }}
    >
      <App />
    </ConfigProvider>
  </StrictMode>,
);
