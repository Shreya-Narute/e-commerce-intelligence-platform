import React, { useEffect, useState } from 'react';
import { Table, ChevronLeft, ChevronRight, Database } from 'lucide-react';
import { LoadingState } from '../components/LoadingState';
import { ErrorState } from '../components/ErrorState';
import { EmptyState } from '../components/EmptyState';
import { getTables, getTableData, TableInfo, TableDataResponse } from '../services/dataExplorerService';

const PAGE_SIZE = 20;

export const DataExplorer: React.FC = () => {
  const [tables, setTables] = useState<TableInfo[]>([]);
  const [selectedTable, setSelectedTable] = useState<string>('');
  const [tableData, setTableData] = useState<TableDataResponse | null>(null);
  const [page, setPage] = useState(1);
  const [loadingTables, setLoadingTables] = useState(true);
  const [loadingData, setLoadingData] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dataError, setDataError] = useState<string | null>(null);

  const fetchTables = async () => {
    setLoadingTables(true);
    setError(null);
    try {
      const t = await getTables();
      setTables(t);
      if (t.length > 0) setSelectedTable(t[0].name);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load table list';
      setError(msg);
    } finally {
      setLoadingTables(false);
    }
  };

  const fetchTableData = async (tableName: string, p: number) => {
    setLoadingData(true);
    setDataError(null);
    try {
      const data = await getTableData(tableName, p, PAGE_SIZE);
      setTableData(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load table data';
      setDataError(msg);
    } finally {
      setLoadingData(false);
    }
  };

  useEffect(() => { fetchTables(); }, []);

  useEffect(() => {
    if (selectedTable) {
      setPage(1);
      fetchTableData(selectedTable, 1);
    }
  }, [selectedTable]);

  const handlePage = (newPage: number) => {
    setPage(newPage);
    fetchTableData(selectedTable, newPage);
  };

  if (loadingTables) return <LoadingState message="Loading Data Explorer..." subtext="Fetching available database tables" />;
  if (error) return <ErrorState title="Data Explorer Unavailable" message={error} onRetry={fetchTables} />;
  if (tables.length === 0) {
    return (
      <EmptyState
        title="No Tables Available"
        description="No database tables found. Ensure the database schema is initialised."
        stageBadge="Data Explorer"
        actionText="View Data Quality"
        actionLink="/data-quality"
        icon={<Table className="h-7 w-7 text-indigo-400" />}
      />
    );
  }

  const totalPages = tableData ? Math.ceil(tableData.total / PAGE_SIZE) : 1;
  const selectedInfo = tables.find((t) => t.name === selectedTable);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="pb-2 border-b border-slate-800">
        <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 mb-2">
          Data Explorer
        </div>
        <h2 className="text-xl font-bold text-white tracking-tight">Interactive Data Explorer</h2>
        <p className="text-xs text-slate-400 mt-0.5">Browse raw database records across all Olist tables.</p>
      </div>

      {/* Table Selector */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-2">
          <Database className="h-4 w-4 text-indigo-400" />
          <span className="text-xs text-slate-400 font-medium">Select Table:</span>
        </div>
        <select
          value={selectedTable}
          onChange={(e) => setSelectedTable(e.target.value)}
          className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-indigo-500"
        >
          {tables.map((t) => (
            <option key={t.name} value={t.name}>
              {t.name} ({t.row_count.toLocaleString()} rows)
            </option>
          ))}
        </select>
        {selectedInfo && (
          <span className="px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-[11px] text-slate-300">
            {selectedInfo.row_count.toLocaleString()} total rows
          </span>
        )}
      </div>

      {/* Table Data */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-white font-mono">{selectedTable}</h3>
          {loadingData && <span className="text-[11px] text-slate-400">Loading…</span>}
        </div>

        {dataError ? (
          <div className="p-5">
            <ErrorState title="Table Data Error" message={dataError} onRetry={() => fetchTableData(selectedTable, page)} />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left text-slate-300">
              <thead className="bg-slate-950/80 text-[11px] uppercase tracking-wider text-slate-400 border-b border-slate-800">
                <tr>
                  {tableData?.columns.map((col) => (
                    <th key={col} className="py-3 px-4 whitespace-nowrap">{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {tableData?.rows.map((row, i) => (
                  <tr key={i} className="hover:bg-slate-800/30">
                    {tableData.columns.map((col) => (
                      <td key={col} className="py-2.5 px-4 font-mono truncate max-w-[200px]">
                        {row[col] === null || row[col] === undefined ? (
                          <span className="text-slate-600">null</span>
                        ) : (
                          String(row[col])
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        <div className="p-4 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
          <span>
            Page {page} of {totalPages || 1}{' '}
            {tableData && <span>({tableData.total.toLocaleString()} total rows)</span>}
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => handlePage(page - 1)}
              disabled={page <= 1 || loadingData}
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            <button
              onClick={() => handlePage(page + 1)}
              disabled={page >= totalPages || loadingData}
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
