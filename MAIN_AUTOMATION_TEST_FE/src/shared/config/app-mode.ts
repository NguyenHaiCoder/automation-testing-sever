/** Production / public deploy — ẩn Quản lý test case & Quản lý log (build .env.production). */
export const RESTRICT_ADMIN =
  import.meta.env.VITE_RESTRICT_ADMIN === 'true' || import.meta.env.VITE_RESTRICT_ADMIN === '1';

export const ADMIN_CONTACT_MESSAGE = 'Vui lòng liên hệ admin';
