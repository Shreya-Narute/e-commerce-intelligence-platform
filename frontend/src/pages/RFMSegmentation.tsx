import React, { useEffect, useState } from 'react';
import {
  BarChart,
  Bar,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { Grid3X3 } from 'lucide-react';
import { LoadingState } from '../components/LoadingState';
import { ErrorState } from '../components/ErrorState';
import { EmptyState } from '../components/EmptyState';
import { getRFMSegments, getRFMCustomers } from '../services/rfmService';
import { RFMSegment, RFMCustomer, RFMSummary } from '../types/rfm';

const SEGMENT_COLORS: Record<string, string> = {
  Champions: '#6366f1',
  'Loyal Customers': '#10b981',
  'Potential Loyalists': '#22d3ee',
  'At Risk': '#f59e0b',
  'Need Attention': '#f97316',
  'Hibernating': '#94a3b8',
  "Can't Lose Them": '#e879f9',
  'New Customers': '#34d399',
  Promising: '#60a5fa',
  'About to Sleep': '#fb923c',
};

const getColor = (segment: string) => SEGMENT_COLORS[segment] ?? '#6366f1';

const fmtCurrency = (v: number) =>
  new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(v);

export const RFMSegmentation: React.FC = () => {
  const [rfmSummary, setRfmSummary] = useState<RFMSummary | null>(null);
  const [customers, setCustomers] = useState<RFMCustomer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAll = async () => {
    setLoading(true);
    setError(null);
    try {
      const [summary, cust] = await Promise.all([
        getRFMSegments(),
        getRFMCustomers(1, 50),
      ]);
      setRfmSummary(summary);
      setCustomers(cust.customers);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load RFM data';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAll(); }, []);

  if (loading) return <LoadingState message="Loading RFM Segmentation..." subtext="Computing Recency, Frequency & Monetary scores" />;
  if (error) return <ErrorState title="RFM Data Unavailable" message={error} onRetry={fetchAll} />;
  if (rfmSummary?.status === 'no_data' || rfmSummary?.status === 'insufficient_data') {
    return (
      <EmptyState
        title="Insufficient Data for RFM Segmentation"
        description="RFM analysis requires populated orders and order_payments tables. Ingest the Olist dataset first."
        stageBadge="RFM Segmentation"
        actionText="View Data Quality"
        actionLink="/data-quality"
        icon={<Grid3X3 className="h-7 w-7 text-indigo-400" />}
      />
    );
  }

  const segments: RFMSegment[] = rfmSummary?.segments ?? [];
  const silhouette = rfmSummary?.silhouette_score;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="pb-2 border-b border-slate-800">
        <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 mb-2">
          RFM Segmentation
        </div>
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight">RFM Customer Segmentation</h2>
            <p className="text-xs text-slate-400 mt-0.5">Recency, Frequency & Monetary value analysis across {rfmSummary?.total_customers?.toLocaleString()} customers.</p>
          </div>
          {silhouette !== null && silhouette !== undefined && (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-indigo-950/40 border border-indigo-800/40">
              <span className="text-[11px] text-slate-400">Silhouette Score</span>
              <span className="text-sm font-bold text-indigo-300">{silhouette.toFixed(3)}</span>
            </div>
          )}
        </div>
      </div>

      {/* Segment Size Bar Chart */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5">
        <h3 className="text-sm font-semibold text-white mb-4">Segment Size Distribution</h3>
        {segments.length === 0 ? (
          <p className="text-xs text-slate-400">No segment data available.</p>
        ) : (
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={segments} margin={{ top: 4, right: 16, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="segment" tick={{ fill: '#94a3b8', fontSize: 10 }} tickLine={false} axisLine={false} />
                <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={false} tickFormatter={(v) => v.toLocaleString()} />
                <Tooltip
                  contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8, fontSize: 12 }}
                  formatter={(v: number) => [v.toLocaleString(), 'Customers']}
                />
                <Bar dataKey="customer_count" radius={[4, 4, 0, 0]}>
                  {segments.map((seg, i) => (
                    <Cell key={i} fill={getColor(seg.segment)} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Segment Table + Scatter row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Segment Summary Table */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden">
          <div className="p-5 border-b border-slate-800">
            <h3 className="text-sm font-semibold text-white">Segment Summary</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left text-slate-300">
              <thead className="bg-slate-950/80 text-[11px] uppercase tracking-wider text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4">Segment</th>
                  <th className="py-3 px-4">Customers</th>
                  <th className="py-3 px-4">Avg R</th>
                  <th className="py-3 px-4">Avg F</th>
                  <th className="py-3 px-4">Avg M</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {segments.map((seg, i) => (
                  <tr key={i} className="hover:bg-slate-800/30">
                    <td className="py-2.5 px-4 flex items-center gap-2">
                      <span className="inline-block w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ background: getColor(seg.segment) }} />
                      <span className="font-medium text-slate-200">{seg.segment}</span>
                    </td>
                    <td className="py-2.5 px-4 font-mono">{seg.customer_count.toLocaleString()}</td>
                    <td className="py-2.5 px-4 font-mono">{seg.avg_recency_days.toFixed(0)}</td>
                    <td className="py-2.5 px-4 font-mono">{seg.avg_frequency.toFixed(1)}</td>
                    <td className="py-2.5 px-4 font-mono">{fmtCurrency(seg.avg_monetary)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* R vs M Scatter */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5">
          <h3 className="text-sm font-semibold text-white mb-4">Recency vs Monetary (Sample)</h3>
          {customers.length === 0 ? (
            <p className="text-xs text-slate-400">No customer scatter data available.</p>
          ) : (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 4, right: 16, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="recency_days" name="Recency (days)" tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={false} label={{ value: 'Recency (days)', position: 'insideBottom', fill: '#64748b', fontSize: 11, dy: 8 }} />
                  <YAxis dataKey="monetary" name="Monetary" tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={false} tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`} />
                  <Tooltip
                    contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8, fontSize: 12 }}
                    formatter={(v: number, name: string) => [
                      name === 'Monetary' ? fmtCurrency(v) : v,
                      name,
                    ]}
                  />
                  {segments.map((seg) => {
                    const segCustomers = customers.filter((c) => c.segment === seg.segment);
                    return (
                      <Scatter
                        key={seg.segment}
                        name={seg.segment}
                        data={segCustomers}
                        fill={getColor(seg.segment)}
                        opacity={0.7}
                      />
                    );
                  })}
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
