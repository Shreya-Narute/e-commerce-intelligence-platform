import React, { useEffect, useState } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { Store, DollarSign } from 'lucide-react';
import { StatCard } from '../components/StatCard';
import { LoadingState } from '../components/LoadingState';
import { ErrorState } from '../components/ErrorState';
import { EmptyState } from '../components/EmptyState';
import { getSellerSummary, getTopRevenueSellers, getSellersByState } from '../services/sellersService';
import { SellerSummary, TopSeller, SellerByState } from '../types/sellers';

const fmtCurrency = (v: number) =>
  new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(v);

export const SellerAnalytics: React.FC = () => {
  const [summary, setSummary] = useState<SellerSummary | null>(null);
  const [topSellers, setTopSellers] = useState<TopSeller[]>([]);
  const [byState, setByState] = useState<SellerByState[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAll = async () => {
    setLoading(true);
    setError(null);
    try {
      const [s, t, st] = await Promise.all([
        getSellerSummary(),
        getTopRevenueSellers(),
        getSellersByState(),
      ]);
      setSummary(s);
      setTopSellers(t.slice(0, 20));
      setByState(st);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load seller data';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAll(); }, []);

  if (loading) return <LoadingState message="Loading Seller Analytics..." subtext="Analysing seller revenue and performance data" />;
  if (error) return <ErrorState title="Seller Data Unavailable" message={error} onRetry={fetchAll} />;
  if (summary?.status === 'no_data') {
    return (
      <EmptyState
        title="No Seller Data Available"
        description="The sellers and order_items tables are empty. Run the ingestion pipeline first."
        stageBadge="Seller Analytics"
        actionText="View Data Quality"
        actionLink="/data-quality"
        icon={<Store className="h-7 w-7 text-indigo-400" />}
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="pb-2 border-b border-slate-800">
        <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 mb-2">
          Seller Intelligence
        </div>
        <h2 className="text-xl font-bold text-white tracking-tight">Seller Performance Analysis</h2>
        <p className="text-xs text-slate-400 mt-0.5">Revenue concentration, top performers, and geographic distribution of sellers.</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <StatCard
          label="Total Sellers"
          value={(summary?.total_sellers ?? 0).toLocaleString()}
          subtext="Active marketplace sellers"
          icon={<Store className="h-4 w-4" />}
          variant="info"
        />
        <StatCard
          label="Avg Revenue / Seller"
          value={fmtCurrency(summary?.avg_revenue_per_seller ?? 0)}
          subtext="Average gross revenue"
          icon={<DollarSign className="h-4 w-4" />}
          variant="success"
        />
      </div>

      {/* Top Sellers Table */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden">
        <div className="p-5 border-b border-slate-800">
          <h3 className="text-sm font-semibold text-white">Top 20 Sellers by Revenue</h3>
        </div>
        <div className="overflow-x-auto max-h-80 overflow-y-auto">
          <table className="w-full text-xs text-left text-slate-300">
            <thead className="bg-slate-950/80 text-[11px] uppercase tracking-wider text-slate-400 border-b border-slate-800 sticky top-0">
              <tr>
                <th className="py-3 px-4">#</th>
                <th className="py-3 px-4">Seller ID</th>
                <th className="py-3 px-4">State</th>
                <th className="py-3 px-4">Revenue</th>
                <th className="py-3 px-4">Orders</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {topSellers.map((s, i) => (
                <tr key={i} className="hover:bg-slate-800/30">
                  <td className="py-2.5 px-4 text-slate-500 font-mono">{i + 1}</td>
                  <td className="py-2.5 px-4 font-mono text-slate-300">{s.seller_id.substring(0, 12)}…</td>
                  <td className="py-2.5 px-4 font-mono">{s.seller_state}</td>
                  <td className="py-2.5 px-4 font-mono">{fmtCurrency(s.revenue)}</td>
                  <td className="py-2.5 px-4 font-mono">{s.order_count.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Sellers by State */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5">
        <h3 className="text-sm font-semibold text-white mb-4">Sellers by State</h3>
        {byState.length === 0 ? (
          <p className="text-xs text-slate-400">No state data available.</p>
        ) : (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={byState} margin={{ top: 4, right: 16, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="state" tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={false} />
                <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={false} tickFormatter={(v) => v.toLocaleString()} />
                <Tooltip
                  contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8, fontSize: 12 }}
                  formatter={(v: number) => [v.toLocaleString(), 'Sellers']}
                />
                <Bar dataKey="seller_count" fill="#6366f1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
};
