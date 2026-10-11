import React from 'react';
import { useHealth } from '../hooks/useHealth';
import { useAuth } from '../hooks/useAuth';
import { Server, Shield, Database, RefreshCw } from 'lucide-react';

export const Settings: React.FC = () => {
  const { data: health, isLoading, refetch } = useHealth();
  const { user } = useAuth();

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div className="pb-2 border-b border-slate-800 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">Platform Settings & Diagnostics</h2>
          <p className="text-xs text-slate-400 mt-0.5">
            System configuration, active environment variables, and authentication parameters.
          </p>
        </div>
        <button
          onClick={() => refetch()}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      <div className="space-y-4 text-xs">
        {/* Backend Connectivity */}
        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800">
          <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
            <Server className="h-4 w-4 text-indigo-400" />
            Backend API Configuration
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-slate-300">
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-[11px] text-slate-400 block">API Base URL</span>
              <span className="font-mono text-indigo-400 mt-1 block">
                {import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'}
              </span>
            </div>
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-[11px] text-slate-400 block">Environment</span>
              <span className="font-mono text-emerald-400 mt-1 block">
                {health?.system.environment || 'development'}
              </span>
            </div>
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-[11px] text-slate-400 block">Python Runtime</span>
              <span className="font-mono text-slate-200 mt-1 block">
                {health?.system.python_version || 'Detecting...'}
              </span>
            </div>
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-[11px] text-slate-400 block">Debug Mode</span>
              <span className="font-mono text-amber-400 mt-1 block">
                {health?.system.debug ? 'True (Development)' : 'False (Production)'}
              </span>
            </div>
          </div>
        </div>

        {/* Database */}
        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800">
          <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
            <Database className="h-4 w-4 text-indigo-400" />
            PostgreSQL Connection Telemetry
          </h3>
          <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Heartbeat Status:</span>
              <span className="font-medium text-emerald-400">
                {health?.database.connected ? 'Operational' : 'Disconnected'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Measured Query Latency:</span>
              <span className="font-mono text-slate-200">{health?.database.latency_ms ?? 0} ms</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Database Engine:</span>
              <span className="font-mono text-slate-300">PostgreSQL 16 (SQLAlchemy 2.0 ORM)</span>
            </div>
          </div>
        </div>

        {/* Current Auth Profile */}
        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800">
          <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
            <Shield className="h-4 w-4 text-indigo-400" />
            Active Session & Security
          </h3>
          <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Active User:</span>
              <span className="text-slate-200 font-medium">{user?.full_name || 'Anonymous User'}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Email:</span>
              <span className="font-mono text-slate-300">{user?.email || 'N/A'}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Security Standard:</span>
              <span className="font-mono text-indigo-400">JWT (HS256) + Bcrypt Salted Hashes</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
