import React, { useState } from 'react';
import { useDataQuality } from '../hooks/useDataQuality';
import { StatCard } from '../components/StatCard';
import { LoadingState } from '../components/LoadingState';
import { ErrorState } from '../components/ErrorState';
import { Badge } from '../components/Badge';
import {
  FileCheck2,
  Database,
  FileSpreadsheet,
  AlertTriangle,
  RefreshCw,
  ChevronDown,
  ChevronUp,
  CheckCircle,
  XCircle,
  Layers,
} from 'lucide-react';

export const DataQuality: React.FC = () => {
  const { data: report, isLoading, error, refetch } = useDataQuality();
  const [expandedTable, setExpandedTable] = useState<string | null>(null);

  if (isLoading && !report) {
    return (
      <LoadingState
        message="Auditing Dataset & PostgreSQL Tables..."
        subtext="Inspecting physical CSV files in data/raw/ and querying schema tables"
      />
    );
  }

  if (error && !report) {
    return (
      <ErrorState
        title="Failed to Retrieve Data Quality Audit"
        message={error}
        onRetry={refetch}
      />
    );
  }

  const toggleExpand = (tableName: string) => {
    setExpandedTable((curr) => (curr === tableName ? null : tableName));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 mb-2">
            Real Schema & Dataset Audit
          </div>
          <h2 className="text-xl font-bold text-white tracking-tight">Data Quality & Schema Health</h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Verifies raw CSV immutability, relational table existence, row counts, and column null rates.
          </p>
        </div>

        <button
          onClick={() => refetch()}
          disabled={isLoading}
          className="inline-flex items-center gap-2 px-3.5 py-2 text-xs font-medium rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? 'animate-spin' : ''}`} />
          Refresh Audit
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Pipeline Status"
          value={report?.status === 'operational' ? 'Operational' : 'Pending Ingestion'}
          subtext={report?.pipeline_stage}
          icon={<FileCheck2 className="h-4 w-4" />}
          variant={report?.status === 'operational' ? 'success' : 'warning'}
        />
        <StatCard
          label="Schema Tables"
          value={`${report?.total_tables ?? 9} Defined`}
          subtext={`${report?.populated_tables ?? 0} populated`}
          icon={<Database className="h-4 w-4" />}
          variant="info"
        />
        <StatCard
          label="Total Rows Ingested"
          value={(report?.total_records ?? 0).toLocaleString()}
          subtext="Actual SQL count across tables"
          icon={<Layers className="h-4 w-4" />}
          variant={report && report.total_records > 0 ? 'success' : 'default'}
        />
        <StatCard
          label="Raw CSV Files"
          value={`${report?.raw_files_found ?? 0} / ${report?.raw_files_total ?? 9}`}
          subtext="Detected in data/raw/"
          icon={<FileSpreadsheet className="h-4 w-4" />}
          variant={report && report.raw_files_found === 9 ? 'success' : 'warning'}
        />
      </div>

      {/* Warnings / Pipeline Alerts */}
      {report && report.warnings.length > 0 && (
        <div className="p-4 rounded-xl bg-amber-950/20 border border-amber-900/40 text-amber-200 text-xs space-y-2">
          <div className="flex items-center gap-2 font-semibold text-amber-300">
            <AlertTriangle className="h-4 w-4 text-amber-400" />
            <span>Pipeline Audit Notices ({report.warnings.length})</span>
          </div>
          <ul className="list-disc list-inside space-y-1 text-amber-300/80 pl-1">
            {report.warnings.map((warn, i) => (
              <li key={i}>{warn}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Database Tables Audit Table */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden">
        <div className="p-5 border-b border-slate-800 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-white">PostgreSQL Schema Tables</h3>
            <p className="text-[11px] text-slate-400 mt-0.5">
              Click a table to inspect column data types, nullability, and verified null rates.
            </p>
          </div>
          <span className="text-xs text-slate-400 font-mono">
            {report?.tables.length ?? 0} Tables Registered
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950/80 text-[11px] uppercase tracking-wider text-slate-400 border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Table Name</th>
                <th className="py-3 px-4">Row Count</th>
                <th className="py-3 px-4">Columns</th>
                <th className="py-3 px-4">Completeness Score</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {report?.tables.map((table) => {
                const isExpanded = expandedTable === table.table_name;
                return (
                  <React.Fragment key={table.table_name}>
                    <tr
                      onClick={() => toggleExpand(table.table_name)}
                      className="hover:bg-slate-800/40 cursor-pointer transition-colors"
                    >
                      <td className="py-3.5 px-4 font-mono font-medium text-white flex items-center gap-2">
                        <Database className="h-3.5 w-3.5 text-indigo-400" />
                        {table.table_name}
                      </td>
                      <td className="py-3.5 px-4 font-mono">
                        {table.row_count.toLocaleString()}
                      </td>
                      <td className="py-3.5 px-4 font-mono text-slate-400">
                        {table.column_count}
                      </td>
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-2">
                          <div className="w-24 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                            <div
                              className={`h-full ${
                                table.completeness_score > 90
                                  ? 'bg-emerald-500'
                                  : table.completeness_score > 50
                                  ? 'bg-amber-500'
                                  : 'bg-slate-700'
                              }`}
                              style={{ width: `${table.completeness_score}%` }}
                            />
                          </div>
                          <span className="font-mono text-[11px]">
                            {table.row_count > 0 ? `${table.completeness_score}%` : 'N/A (0 rows)'}
                          </span>
                        </div>
                      </td>
                      <td className="py-3.5 px-4">
                        <Badge
                          variant={
                            table.status === 'populated'
                              ? 'healthy'
                              : table.status === 'empty'
                              ? 'neutral'
                              : 'degraded'
                          }
                        >
                          {table.status}
                        </Badge>
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <button
                          type="button"
                          className="p-1 rounded text-slate-400 hover:text-white"
                        >
                          {isExpanded ? (
                            <ChevronUp className="h-4 w-4" />
                          ) : (
                            <ChevronDown className="h-4 w-4" />
                          )}
                        </button>
                      </td>
                    </tr>

                    {/* Column drilldown */}
                    {isExpanded && (
                      <tr className="bg-slate-950/60">
                        <td colSpan={6} className="p-4">
                          <div className="rounded-lg border border-slate-800 bg-slate-900/80 p-4">
                            <h4 className="text-xs font-semibold text-slate-200 mb-3">
                              Column Schema & Integrity Metrics: <span className="font-mono text-indigo-400">{table.table_name}</span>
                            </h4>
                            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2.5 text-xs">
                              {table.columns.map((col) => (
                                <div
                                  key={col.name}
                                  className="p-2.5 rounded-lg bg-slate-950 border border-slate-800/80 flex flex-col justify-between"
                                >
                                  <div className="flex items-center justify-between">
                                    <span className="font-mono text-slate-200 truncate">{col.name}</span>
                                    <span className="text-[10px] text-slate-400 uppercase font-mono">
                                      {col.data_type}
                                    </span>
                                  </div>
                                  <div className="mt-2 flex items-center justify-between text-[11px] text-slate-400">
                                    <span>Nullable: {col.nullable ? 'Yes' : 'No (Required)'}</span>
                                    {table.row_count > 0 && (
                                      <span className="font-mono text-slate-300">
                                        Null: {col.null_count} ({col.null_percentage}%)
                                      </span>
                                    )}
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Raw Files Audit Section */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden">
        <div className="p-5 border-b border-slate-800">
          <h3 className="text-sm font-semibold text-white">Raw File Immutability & Presence</h3>
          <p className="text-[11px] text-slate-400 mt-0.5">
            Physical files tracked in <code className="text-indigo-400">data/raw/</code> for immutable ETL processing.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 p-5">
          {report?.raw_files.map((file) => (
            <div
              key={file.filename}
              className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between gap-2"
            >
              <div className="flex items-center gap-2.5 truncate">
                {file.exists ? (
                  <CheckCircle className="h-4 w-4 text-emerald-400 flex-shrink-0" />
                ) : (
                  <XCircle className="h-4 w-4 text-slate-400 flex-shrink-0" />
                )}
                <div className="flex flex-col truncate">
                  <span className="text-xs font-mono text-slate-200 truncate">{file.filename}</span>
                  <span className="text-[10px] text-slate-400">{file.size_readable}</span>
                </div>
              </div>

              <Badge variant={file.exists ? 'healthy' : 'neutral'}>
                {file.exists ? 'Ready' : 'Missing'}
              </Badge>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
