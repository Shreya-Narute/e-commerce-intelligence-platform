import React, { useEffect, useState } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { Truck, Star, Clock } from 'lucide-react';
import { StatCard } from '../components/StatCard';
import { LoadingState } from '../components/LoadingState';
import { ErrorState } from '../components/ErrorState';
import { EmptyState } from '../components/EmptyState';
import { getDeliverySummary, getDeliveryByState, getReviewDistribution, getLateAnalysis } from '../services/deliveryService';
import { DeliverySummary, DeliveryByState, ReviewDistribution, LateAnalysis } from '../types/delivery';

const REVIEW_COLORS = ['#f43f5e', '#f97316', '#f59e0b', '#22d3ee', '#10b981'];

export const DeliveryAndSatisfaction: React.FC = () => {
  const [summary, setSummary] = useState<DeliverySummary | null>(null);
  const [byState, setByState] = useState<DeliveryByState[]>([]);
  const [reviews, setReviews] = useState<ReviewDistribution[]>([]);
  const [lateAnalysis, setLateAnalysis] = useState<LateAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAll = async () => {
    setLoading(true);
    setError(null);
    try {
      const [s, st, r, l] = await Promise.all([
        getDeliverySummary(),
        getDeliveryByState(),
        getReviewDistribution(),
        getLateAnalysis(),
      ]);
      setSummary(s);
      setByState(st.slice(0, 15));
      setReviews(r);
      setLateAnalysis(l);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load delivery data';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAll(); }, []);

  if (loading) return <LoadingState message="Loading Delivery & Satisfaction..." subtext="Analysing delivery times and review scores" />;
  if (error) return <ErrorState title="Delivery Data Unavailable" message={error} onRetry={fetchAll} />;
  if (summary?.status === 'no_data') {
    return (
      <EmptyState
        title="No Delivery Data Available"
        description="The orders and order_reviews tables are empty. Run the ingestion pipeline first."
        stageBadge="Delivery & Satisfaction"
        actionText="View Data Quality"
        actionLink="/data-quality"
        icon={<Truck className="h-7 w-7 text-indigo-400" />}
      />
    );
  }

  const onTimeRate = (summary?.on_time_rate ?? 0).toFixed(1);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="pb-2 border-b border-slate-800">
        <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 mb-2">
          Delivery & Satisfaction
        </div>
        <h2 className="text-xl font-bold text-white tracking-tight">Delivery Performance & Customer Satisfaction</h2>
        <p className="text-xs text-slate-400 mt-0.5">Delivery timing, on-time rates, and customer review scores.</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatCard
          label="Avg Delivery Days"
          value={`${(summary?.avg_delivery_days ?? 0).toFixed(1)} days`}
          subtext="Estimated to delivered"
          icon={<Clock className="h-4 w-4" />}
          variant="info"
        />
        <StatCard
          label="On-Time Delivery Rate"
          value={`${onTimeRate}%`}
          subtext="Delivered on or before estimate"
          icon={<Truck className="h-4 w-4" />}
          variant={parseFloat(onTimeRate) >= 80 ? 'success' : 'warning'}
        />
        <StatCard
          label="Avg Review Score"
          value={`${(summary?.avg_review_score ?? 0).toFixed(2)} / 5`}
          subtext="Customer satisfaction rating"
          icon={<Star className="h-4 w-4" />}
          variant={(summary?.avg_review_score ?? 0) >= 4 ? 'success' : 'warning'}
        />
      </div>

      {/* Review Distribution + Late Analysis row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Review Score Distribution */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5">
          <h3 className="text-sm font-semibold text-white mb-4">Review Score Distribution (1–5)</h3>
          {reviews.length === 0 ? (
            <p className="text-xs text-slate-400">No review data available.</p>
          ) : (
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={reviews} margin={{ top: 4, right: 16, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="score" tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={false} label={{ value: 'Score', position: 'insideBottom', fill: '#64748b', fontSize: 11, dy: 8 }} />
                  <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={false} tickFormatter={(v) => v.toLocaleString()} />
                  <Tooltip
                    contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8, fontSize: 12 }}
                    formatter={(v: number) => [v.toLocaleString(), 'Reviews']}
                  />
                  <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                    {reviews.map((_, i) => (
                      <Cell key={i} fill={REVIEW_COLORS[i % REVIEW_COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        {/* Late vs On-Time */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5">
          <h3 className="text-sm font-semibold text-white mb-4">Late vs On-Time Deliveries</h3>
          {!lateAnalysis ? (
            <p className="text-xs text-slate-400">No late analysis data available.</p>
          ) : (
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={[
                    { category: 'On Time', count: lateAnalysis.on_time_count, fill: '#10b981' },
                    { category: 'Late',    count: lateAnalysis.late_count,    fill: '#f43f5e' },
                  ]}
                  margin={{ top: 4, right: 16, left: 0, bottom: 0 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="category" tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={false} />
                  <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={false} tickFormatter={(v) => v.toLocaleString()} />
                  <Tooltip
                    contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8, fontSize: 12 }}
                    formatter={(v: number) => [v.toLocaleString(), 'Orders']}
                  />
                  <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                    {[{ fill: '#10b981' }, { fill: '#f43f5e' }].map((entry, i) => (
                      <Cell key={i} fill={entry.fill} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
              <div className="mt-3 grid grid-cols-2 gap-3 text-xs text-slate-400">
                <div>On-Time Avg Review: <span className="text-white font-medium">{(lateAnalysis.on_time_avg_review ?? 0).toFixed(2)}</span></div>
                <div>Late Avg Review: <span className="text-white font-medium">{(lateAnalysis.late_avg_review ?? 0).toFixed(2)}</span></div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Avg Delivery by State */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5">
        <h3 className="text-sm font-semibold text-white mb-4">Avg Delivery Days by State (Top 15)</h3>
        {byState.length === 0 ? (
          <p className="text-xs text-slate-400">No state delivery data available.</p>
        ) : (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={byState} margin={{ top: 4, right: 16, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="state" tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={false} />
                <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={false} />
                <Tooltip
                  contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8, fontSize: 12 }}
                  formatter={(v: number) => [`${v.toFixed(1)} days`, 'Avg Delivery']}
                />
                <Bar dataKey="avg_delivery_days" fill="#f59e0b" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
};
