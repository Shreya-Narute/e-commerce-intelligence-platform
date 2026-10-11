import { apiClient } from './api';

export interface TableInfo {
  name: string;
  row_count: number;
}

export interface TableDataResponse {
  columns: string[];
  rows: Record<string, unknown>[];
  total: number;
  page: number;
  page_size: number;
}

// GET /data-explorer/tables → { status, message, data: [{table_name, row_count}] }
export const getTables = async (): Promise<TableInfo[]> => {
  const res = await apiClient.get('/data-explorer/tables');
  return (res.data.data ?? []).map((t: { table_name: string; row_count: number }) => ({
    name: t.table_name,      // API uses table_name, frontend type uses name
    row_count: t.row_count,
  }));
};

// GET /data-explorer/{table}?page=&page_size=
// Response: { status, message, table_name, page, page_size, total_rows, columns, data: [...rows] }
export const getTableData = async (
  tableName: string,
  page: number = 1,
  pageSize: number = 20
): Promise<TableDataResponse> => {
  const res = await apiClient.get(`/data-explorer/${tableName}?page=${page}&page_size=${pageSize}`);
  const body = res.data;
  return {
    columns: body.columns ?? [],
    rows: body.data ?? [],
    total: body.total_rows ?? 0,
    page: body.page ?? page,
    page_size: body.page_size ?? pageSize,
  };
};
