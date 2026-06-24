import type { TablePaginationConfig } from 'antd/es/table';
import { useCallback, useMemo, useState } from 'react';

interface UseTablePaginationOptions {
  defaultPageSize?: number;
  pageSizeOptions?: number[];
  itemLabel?: string;
}

export function useTablePagination({
  defaultPageSize = 15,
  pageSizeOptions = [10, 15, 30, 60],
  itemLabel = 'mục',
}: UseTablePaginationOptions = {}) {
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(defaultPageSize);

  const resetPage = useCallback(() => setPage(1), []);

  const onChange = useCallback((nextPage: number, nextSize: number) => {
    setPage(nextPage);
    setPageSize(nextSize);
  }, []);

  const buildPagination = useCallback(
    (total: number): TablePaginationConfig => ({
      current: page,
      pageSize,
      total,
      showSizeChanger: true,
      pageSizeOptions,
      showTotal: (t, range) => `${range[0]}-${range[1]} / ${t} ${itemLabel}`,
      locale: { items_per_page: '/ trang' },
      onChange,
    }),
    [page, pageSize, pageSizeOptions, itemLabel, onChange],
  );

  return useMemo(
    () => ({ page, pageSize, setPage, setPageSize, resetPage, buildPagination }),
    [page, pageSize, resetPage, buildPagination],
  );
}
