import {
  DashboardOutlined,
  FileTextOutlined,
  FolderOpenOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
} from '@ant-design/icons';
import { Badge, Layout, Menu, Tooltip, Typography } from 'antd';
import { ADMIN_CONTACT_MESSAGE, RESTRICT_ADMIN } from '@/shared/config/app-mode';
import type { AppView } from '@/shared/types/navigation';

const { Sider } = Layout;
const { Text } = Typography;

interface AppSidebarProps {
  collapsed: boolean;
  activeView: AppView;
  onCollapse: (v: boolean) => void;
  onNavigate: (view: AppView) => void;
  caseCount: number;
  logCount?: number;
}

const ADMIN_VIEWS = new Set<AppView>(['manage', 'logs']);

const MENU_ITEMS = [
  { key: 'dashboard' as const, icon: <DashboardOutlined />, label: 'Bảng kiểm thử' },
  { key: 'manage' as const, icon: <FileTextOutlined />, label: 'Quản lý test case' },
  { key: 'logs' as const, icon: <FolderOpenOutlined />, label: 'Quản lý log' },
];

function menuLabel(item: (typeof MENU_ITEMS)[number], caseCount: number, logCount?: number) {
  if (RESTRICT_ADMIN && ADMIN_VIEWS.has(item.key)) {
    return (
      <Tooltip title={ADMIN_CONTACT_MESSAGE}>
        <span className="sider-menu-restricted">{ADMIN_CONTACT_MESSAGE}</span>
      </Tooltip>
    );
  }
  if (item.key === 'manage') {
    return (
      <span>
        {item.label}{' '}
        <Badge count={caseCount} size="small" style={{ backgroundColor: '#1677ff' }} overflowCount={999} />
      </span>
    );
  }
  if (item.key === 'logs' && logCount !== undefined) {
    return (
      <span>
        {item.label} <Badge count={logCount} size="small" overflowCount={999} />
      </span>
    );
  }
  return item.label;
}

export function AppSidebar({ collapsed, activeView, onCollapse, onNavigate, caseCount, logCount }: AppSidebarProps) {
  return (
    <Sider
      className="app-sider"
      collapsible
      collapsed={collapsed}
      onCollapse={onCollapse}
      width={260}
      collapsedWidth={72}
      trigger={null}
      theme="dark"
    >
      <div className="sider-brand">
        <div className="sider-brand-icon">H2Q</div>
        {!collapsed && (
          <div>
            <Text strong style={{ color: '#fff', fontSize: 15 }}>
              Checklist Tester
            </Text>
            <br />
            <Text style={{ color: 'rgba(255,255,255,0.55)', fontSize: 11 }}>Automation Dashboard</Text>
          </div>
        )}
      </div>

      <Menu
        theme="dark"
        mode="inline"
        selectedKeys={[activeView]}
        className="sider-menu"
        items={MENU_ITEMS.map((item) => ({
          key: item.key,
          icon: item.icon,
          label: menuLabel(item, caseCount, logCount),
          disabled: RESTRICT_ADMIN && ADMIN_VIEWS.has(item.key),
          onClick: () => {
            if (RESTRICT_ADMIN && ADMIN_VIEWS.has(item.key)) return;
            onNavigate(item.key);
          },
        }))}
      />

      <div className="sider-footer">
        <button type="button" className="sider-toggle" onClick={() => onCollapse(!collapsed)}>
          {collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
          {!collapsed && <span>Thu gọn</span>}
        </button>
        {!collapsed && (
          <Text style={{ color: 'rgba(255,255,255,0.4)', fontSize: 11, display: 'block', marginTop: 8 }}>
            API: MAIN_AUTOMATION_TEST
          </Text>
        )}
      </div>
    </Sider>
  );
}
