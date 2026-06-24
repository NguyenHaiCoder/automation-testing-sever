/** Application-wide navigation types. */
export type AppView = 'dashboard' | 'manage' | 'logs';

export const APP_VIEW_LABELS: Record<AppView, string> = {
  dashboard: 'Bảng kiểm thử',
  manage: 'Quản lý test case',
  logs: 'Quản lý log',
};
