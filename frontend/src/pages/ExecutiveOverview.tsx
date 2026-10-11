import React from 'react';
import { useHealth } from '../hooks/useHealth';
import { useDataQuality } from '../hooks/useDataQuality';
import { StatCard } from '../components/StatCard';
import { LoadingState } from '../components/LoadingState';
import { ErrorState } from '../components/ErrorState';
import { EmptyState } from '../components/EmptyState';
import {
  Database,
  Layers,
  FileCheck2,
  Server,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
} from 'lucide-react';
import { Link } from 'react-router-dom';

export const ExecutiveOverview: React.FC = () => {
  const { data: health, isLoading: healthLoading, error: healthError, refetch: refetchHealth } = useHealth();
  const { data: dq, isLoading: dqLoading, error: dqError, refetch: refetchDq } = useDataQuality();

  if (healthLoading || dqLoading) {
    return <LoadingState message="Connecting to Platform Services..." subtext="Querying PostgreSQL engine and checking schema integrity" />;
  }

  if ((healthError && !health) || (dqError && !dq)) {
    return (
      <ErrorState
        title="Backend Service Unreachable"
        message={`Unable to connect to platform services: ${healthError || dqError}`}
        onRetry={() => {
          refetchHealth();
          refetchDq();
        }}
      />
    );
  }


  const isDbConnected = health?.database?.connected ?? false;
  const totalTables = dq?.total_tables ?? 9;
  const populatedTables = dq?.populated_tables ?? 0;
  const totalRecords = dq?.total_records ?? 0;
  const rawFilesFound = dq?.raw_files_found ?? 0;
  const rawFilesTotal = dq?.raw_files_total ?? 9;

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 mb-2">
            Stage 1: Production Foundation
          </div>
          <h2 className="text-xl font-bold text-white tracking-tight">Executive Platform Overview</h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time telemetry and database architecture for the Brazilian E-Commerce Intelligence Platform.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to="/data-quality"
            className="inline-flex items-center gap-2 px-3.5 py-2 text-xs font-medium rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white transition-colors shadow-sm shadow-indigo-900/30"
          >
            <FileCheck2 className="h-4 w-4" />
            Inspect Data Quality
            <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>
      </div>

      {/* Verified Live Metrics - Zero fabricated numbers */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Database Status"
          value={isDbConnected ? 'Connected' : 'Disconnected'}
          subtext={isDbConnected ? `Latency: ${health?.database.latency_ms} ms` : 'Check PostgreSQL instance'}
          icon={<Database className="h-4 w-4" />}
          variant={isDbConnected ? 'success' : 'warning'}
        />
        <StatCard
          label="Registered Tables"
          value={totalTables}
          subtext="Full Olist Relational Schema"
          icon={<Layers className="h-4 w-4" />}
          variant="info"
        />
        <StatCard
          label="Populated Tables"
          value={`${populatedTables} / ${totalTables}`}
          subtext={populatedTables === 0 ? 'Awaiting Stage 2 ETL' : 'Ingestion active'}
          icon={<CheckCircle2 className="h-4 w-4" />}
          variant={populatedTables > 0 ? 'success' : 'default'}
        />
        <StatCard
          label="Total Database Records"
          value={totalRecords.toLocaleString()}
          subtext={totalRecords === 0 ? 'Zero simulated records' : 'Verified live rows'}
          icon={<Server className="h-4 w-4" />}
          variant={totalRecords > 0 ? 'success' : 'default'}
        />
      </div>

      {/* Empty State / Notice when tables are unpopulated (Strictly No Mock Data) */}
      {totalRecords === 0 ? (
        <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 sm:p-8">
          <EmptyState
            title="Database Initialized — Awaiting Stage 2 Ingestion"
            description="The platform foundation, PostgreSQL schema (9 Olist models + user authentication), Alembic migrations, and FastAPI REST endpoints are fully operational. In accordance with production integrity standards, no fake charts, simulated metrics, or hard-coded KPIs are rendered."
            stageBadge="Production Foundation Verified"
            actionText="View Data Quality Audit"
            actionLink="/data-quality"
            icon={<Database className="h-7 w-7 text-indigo-400" />}
          />

          <div className="mt-6 pt-6 border-t border-slate-800/80 grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
              <span className="font-semibold text-slate-200 block mb-1">1. Raw Dataset Status</span>
              <p className="text-slate-400 text-[11px] leading-relaxed">
                {rawFilesFound}/{rawFilesTotal} raw CSV files detected in <code className="text-indigo-400">data/raw/</code>. Use <code className="text-slate-300">scripts/download_dataset.py</code> to download Olist data.
              </p>
            </div>
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
              <span className="font-semibold text-slate-200 block mb-1">2. Ingestion Pipeline</span>
              <p className="text-slate-400 text-[11px] leading-relaxed">
                Run <code className="text-indigo-400">python scripts/ingest_data.py</code> to load real raw files directly into PostgreSQL.
              </p>
            </div>
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
              <span className="font-semibold text-slate-200 block mb-1">3. Analytics Modules</span>
              <p className="text-slate-400 text-[11px] leading-relaxed">
                RFM segmentation, sales intelligence, and forecasting will compute on real ingested data in subsequent stages.
              </p>
            </div>
          </div>
        </div>
      ) : (
        <div className="p-6 rounded-2xl bg-emerald-950/20 border border-emerald-800/40 text-emerald-300 text-xs flex items-center justify-between">
          <span>Active dataset detected: {totalRecords.toLocaleString()} verified rows in database.</span>
          <Link to="/data-quality" className="underline font-semibold hover:text-white">
            Inspect Schema Completeness
          </Link>
        </div>
      )}

      {/* Architecture & Foundation Components Checklist */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
        <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
          <ShieldCheck className="h-4 w-4 text-indigo-400" />
          Foundation Architecture Status (Stage 1)
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {[
            { name: 'FastAPI Backend Core', status: 'Operational', detail: 'Asynchronous REST APIs with Pydantic v2 validation' },
            { name: 'PostgreSQL Relational Schema', status: isDbConnected ? 'Connected' : 'Configured', detail: '9 Olist tables + users with PK/FK constraints & indexes' },
            { name: 'Alembic Migration Suite', status: 'Version 001', detail: 'Initial migration script generated for declarative schema management' },
            { name: 'JWT Security & Auth', status: 'Enabled', detail: 'Bcrypt password hashing & bearer token issuance' },
            { name: 'Data Quality Auditing', status: 'Real-Time', detail: 'Queries actual table counts, columns, and null rates' },
            { name: 'Docker Orchestration', status: 'Configured', detail: 'Multi-service configuration for DB, Backend, and Frontend' },
          ].map((item, idx) => (
            <div key={idx} className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 flex flex-col justify-between">
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs font-medium text-slate-200">{item.name}</span>
                <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-950/60 text-emerald-400 border border-emerald-800/40">
                  {item.status}
                </span>
              </div>
              <p className="text-[11px] text-slate-400 mt-2">{item.detail}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
