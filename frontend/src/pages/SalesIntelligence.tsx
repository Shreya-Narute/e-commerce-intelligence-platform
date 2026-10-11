import React, { useEffect, useState } from 'react';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { TrendingUp, DollarSign, ShoppingCart } from 'lucide-react';
import { StatCard } from '../components/StatCard';
import { LoadingState } from '../components/LoadingState';
import { ErrorState } from '../components/ErrorState';
import { EmptyState } from '../components/EmptyState';
import {
  getSalesSummary,
  getMonthlyRevenue,
  getRevenueByState,
  getRevenueByCategory,
  getOrderStatusCounts,
} from '../services/salesService';
import { SalesSummary, MonthlyRevenue, RevenueByState, RevenueByCategory, OrderStatusCount } from '../types/sales';

const CHART_COLORS = ['#6366f1', '#22d3ee', '#f59e0b', '#10b981', '#f43f5e', '#a78bfa', '#34d399', '#fb923c'];

const fmtCurrency = (v: number) =>
  new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(v);

export const SalesIntelligence: React.FC = () => {
  const [summary, setSummary] = useState<SalesSummary | null>(null);
  const [monthly, setMonthly] = useState<MonthlyRevenue[]>([]);
  const [byState, setByState] = useState<RevenueByState[]>([]);
  const [byCategory, setByCategory] = useState<RevenueByCategory[]>([]);
  const [orderStatus, setOrderStatus] = useState<OrderStatusCount[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAll = async () => {
    setLoading(true);
    setError(null);
    try {
      const [s, m, st, cat, os] = await Promise.all([
        getSalesSummary(),
        getMonthlyRevenue(),
        getRevenueByState(),
        getRevenueByCategory(),
        getOrderStatusCounts(),
      ]);
      setSummary(s);
      setMonthly(m);
      setByState(st.slice(0, 10));
      setByCategory(cat.slice(0, 15));
      setOrderStatus(os);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load sales data';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAll(); }, []);

  if (loading) return <LoadingState message="Loading Sales Intelligence..." subtext="Querying revenue, order, and payment data from PostgreSQL" />;
  if (error) return <ErrorState title="Sales Data Unavailable" message={error} onRetry={fetchAll} />;
  if (summary?.status === 'no_data') {
    return (
      <EmptyState
        title="No Sales Data Available"
        description="The orders and order_items tables are empty. Run the ingestion pipeline to load Olist data."
        stageBadge="Sales Intelligence"
        actionText="View Data Quality"
        actionLink="/data-quality"
        icon={<TrendingUp className="h-7 w-7 text-indigo-400" />}
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 mb-2">
            Sales Intelligence
          </div>
          <h2 className="text-xl font-bold text-white tracking-tight">Sales Performance Overview</h2>
          <p className="text-xs text-slate-400 mt-0.5">Revenue trajectory, order volume, and geographic distributions.</p>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatCard
          label="Total Revenue"
          value={fmtCurrency(summary?.total_revenue ?? 0)}
          subtext="Gross Merchandise Value"
          icon={<DollarSign className="h-4 w-4" />}
          variant="success"
        />
        <StatCard
          label="Total Orders"
          value={(summary?.total_orders ?? 0).toLocaleString()}
          subtext="Completed & delivered orders"
          icon={<ShoppingCart className="h-4 w-4" />}
          variant="info"
        />
        <StatCard
          label="Avg Order Value"
          value={fmtCurrency(summary?.avg_order_value ?? 0)}
          subtext="Average per transaction"
          icon={<TrendingUp className="h-4 w-4" />}
          variant="default"
        />
      </div>

      {/* Monthly Revenue Area Chart */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5">
        <h3 className="text-sm font-semibold text-white mb-4">Monthly Revenue Trend</h3>
        {monthly.length === 0 ? (
          <p className="text-xs text-slate-400">No monthly data available.</p>
        ) : (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={monthly} margin={{ top: 4, right: 16, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="revenueGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="month" tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={false} />
                <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={false} tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`} />
                <Tooltip
                  contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8, fontSize: 12 }}
                  labelStyle={{ color: '#e2e8f0' }}
                  formatter={(v: number) => [fmtCurrency(v), 'Revenue']}
                />
                <Area type="monotone" dataKey="revenue" stroke="#6366f1" strokeWidth={2} fill="url(#revenueGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* State & Category charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue by State */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5">
          <h3 className="text-sm font-semibold text-white mb-4">Revenue by State (Top 10)</h3>
          {byState.length === 0 ? (
            <p className="text-xs text-slate-400">No state data available.</p>
          ) : (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={byState} margin={{ top: 4, right: 16, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="state" tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={false} />
                  <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={false} tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`} />
                  <Tooltip
                    contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8, fontSize: 12 }}
                    formatter={(v: number) => [fmtCurrency(v), 'Revenue']}
                  />
                  <Bar dataKey="revenue" fill="#6366f1" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        {/* Order Status Pie */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5">
          <h3 className="text-sm font-semibold text-white mb-4">Order Status Distribution</h3>
          {orderStatus.length === 0 ? (
            <p className="text-xs text-slate-400">No status data available.</p>
          ) : (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={orderStatus}
                    dataKey="count"
                    nameKey="status"
                    cx="50%"
                    cy="50%"
                    outerRadius={90}
                    label={({ status, percent }) => `${status} ${(percent * 100).toFixed(0)}%`}
                    labelLine={false}
                  >
                    {orderStatus.map((_, i) => (
                      <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8, fontSize: 12 }}
                  />
                  <Legend wrapperStyle={{ fontSize: 11, color: '#94a3b8' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      </div>

      {/* Revenue by Category */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5">
        <h3 className="text-sm font-semibold text-white mb-4">Revenue by Category (Top 15)</h3>
        {byCategory.length === 0 ? (
          <p className="text-xs text-slate-400">No category data available.</p>
        ) : (
          <div className="h-96">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={byCategory}
                layout="vertical"
                margin={{ top: 4, right: 24, left: 120, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                <XAxis type="number" tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={false} tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`} />
                <YAxis type="category" dataKey="category" tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={false} width={115} />
                <Tooltip
                  contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8, fontSize: 12 }}
                  formatter={(v: number) => [fmtCurrency(v), 'Revenue']}
                />
                <Bar dataKey="revenue" fill="#22d3ee" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
};
