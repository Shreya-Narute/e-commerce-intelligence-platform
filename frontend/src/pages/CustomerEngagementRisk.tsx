import React, { useEffect, useState } from 'react';
import { AlertOctagon, ChevronLeft, ChevronRight } from 'lucide-react';
import { StatCard } from '../components/StatCard';
import { LoadingState } from '../components/LoadingState';
import { ErrorState } from '../components/ErrorState';
import { EmptyState } from '../components/EmptyState';
import { getRiskSummary, getAtRiskCustomers } from '../services/engagementService';
import { EngagementRiskSummary, AtRiskCustomer } from '../types/engagement';

const TIER_COLOR: Record<string, string> = {
  Active: 'text-emerald-400',
  Cooling: 'text-indigo-400',
  'At Risk': 'text-amber-400',
  Inactive: 'text-slate-400',
};

const PAGE_SIZE = 20;

export const CustomerEngagementRisk: React.FC = () => {
  const [summary, setSummary] = useState<EngagementRiskSummary | null>(null);
  const [customers, setCustomers] = useState<AtRiskCustomer[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [tableLoading, setTableLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSummary = async () => {
    setLoading(true);
    setError(null);
    try {
      const s = await getRiskSummary();
      setSummary(s);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load engagement data';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const fetchCustomers = async (p: number) => {
    setTableLoading(true);
    try {
      const res = await getAtRiskCustomers(p, PAGE_SIZE);
      setCustomers(res.customers);
      setTotal(res.total);
    } catch {
      // table error handled silently; summary still shown
    } finally {
      setTableLoading(false);
    }
  };

  useEffect(() => { fetchSummary(); fetchCustomers(1); }, []);

  const handlePage = (newPage: number) => {
    setPage(newPage);
    fetchCustomers(newPage);
  };

  const totalPages = Math.ceil(total / PAGE_SIZE);

  if (loading) return <LoadingState message="Loading Engagement Risk Analysis..." subtext="Calculating recency-based risk tiers" />;
  if (error) return <ErrorState title="Engagement Data Unavailable" message={error} onRetry={() => { fetchSummary(); fetchCustomers(1); }} />;
  if (summary?.status === 'no_data') {
    return (
      <EmptyState
        title="No Customer Engagement Data"
        description="Orders data is required for engagement risk analysis. Ingest the Olist dataset first."
        stageBadge="Customer Engagement Risk"
        actionText="View Data Quality"
        actionLink="/data-quality"
        icon={<AlertOctagon className="h-7 w-7 text-indigo-400" />}
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="pb-2 border-b border-slate-800">
        <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20 mb-2">
          Engagement Risk (Recency-Based)
        </div>
        <h2 className="text-xl font-bold text-white tracking-tight">Customer Engagement Risk</h2>
        <p className="text-xs text-slate-400 mt-0.5">
          Customers classified by days since last purchase. This is a recency-based engagement tier, not a churn prediction model.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <StatCard label="Active" value={(summary?.active ?? 0).toLocaleString()} subtext="≤ 90 days since purchase" variant="success" />
        <StatCard label="Cooling" value={(summary?.cooling ?? 0).toLocaleString()} subtext="91–180 days" variant="info" />
        <StatCard label="At Risk" value={(summary?.at_risk ?? 0).toLocaleString()} subtext="181–365 days" variant="warning" />
        <StatCard label="Inactive" value={(summary?.inactive ?? 0).toLocaleString()} subtext="> 365 days" variant="default" />
      </div>

      {/* At-Risk Customers Table */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden">
        <div className="p-5 border-b border-slate-800 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-white">At-Risk & Inactive Customers</h3>
            <p className="text-[11px] text-slate-400 mt-0.5">{total.toLocaleString()} customers with reduced engagement</p>
          </div>
          {tableLoading && <span className="text-[11px] text-slate-400">Loading…</span>}
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left text-slate-300">
            <thead className="bg-slate-950/80 text-[11px] uppercase tracking-wider text-slate-400 border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Customer ID</th>
                <th className="py-3 px-4">Last Purchase</th>
                <th className="py-3 px-4">Days Since</th>
                <th className="py-3 px-4">Risk Tier</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {customers.map((c, i) => (
                <tr key={i} className="hover:bg-slate-800/30">
                  <td className="py-2.5 px-4 font-mono text-slate-300 truncate max-w-[140px]">{c.customer_id.substring(0, 12)}…</td>
                  <td className="py-2.5 px-4 font-mono">{c.last_purchase_date?.slice(0, 10) ?? '—'}</td>
                  <td className="py-2.5 px-4 font-mono">{c.days_since_purchase}</td>
                  <td className="py-2.5 px-4">
                    <span className={`font-semibold ${TIER_COLOR[c.risk_tier] ?? 'text-slate-300'}`}>{c.risk_tier}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="p-4 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
          <span>Page {page} of {totalPages || 1} ({total.toLocaleString()} total)</span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => handlePage(page - 1)}
              disabled={page <= 1}
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            <button
              onClick={() => handlePage(page + 1)}
              disabled={page >= totalPages}
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
