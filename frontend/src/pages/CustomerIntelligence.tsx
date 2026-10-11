import React, { useEffect, useState } from 'react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { Users, ShoppingCart, DollarSign } from 'lucide-react';
import { StatCard } from '../components/StatCard';
import { LoadingState } from '../components/LoadingState';
import { ErrorState } from '../components/ErrorState';
import { EmptyState } from '../components/EmptyState';
import { getCustomerSummary, getTopStates, getPurchaseFrequency, getCohort } from '../services/customersService';
import { CustomerSummary, CustomerState, PurchaseFrequency, CustomerCohort } from '../types/customers';

const fmtCurrency = (v: number) =>
  new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(v);

export const CustomerIntelligence: React.FC = () => {
  const [summary, setSummary] = useState<CustomerSummary | null>(null);
  const [states, setStates] = useState<CustomerState[]>([]);
  const [frequency, setFrequency] = useState<PurchaseFrequency[]>([]);
  const [cohort, setCohort] = useState<CustomerCohort[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAll = async () => {
    setLoading(true);
    setError(null);
    try {
      const [s, st, f, c] = await Promise.all([
        getCustomerSummary(),
        getTopStates(),
        getPurchaseFrequency(),
        getCohort(),
      ]);
      setSummary(s);
      setStates(st);
      setFrequency(f);
      setCohort(c);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load customer data';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAll(); }, []);

  if (loading) return <LoadingState message="Loading Customer Intelligence..." subtext="Analysing purchase behaviour and cohort data" />;
  if (error) return <ErrorState title="Customer Data Unavailable" message={error} onRetry={fetchAll} />;
  if (summary?.status === 'no_data') {
    return (
      <EmptyState
        title="No Customer Data Available"
        description="The customers and orders tables are empty. Run the ingestion pipeline first."
        stageBadge="Customer Intelligence"
        actionText="View Data Quality"
        actionLink="/data-quality"
        icon={<Users className="h-7 w-7 text-indigo-400" />}
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="pb-2 border-b border-slate-800">
        <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 mb-2">
          Customer Intelligence
        </div>
        <h2 className="text-xl font-bold text-white tracking-tight">Customer Behaviour Analysis</h2>
        <p className="text-xs text-slate-400 mt-0.5">Acquisition cohorts, purchase patterns, and geographic distribution.</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatCard
          label="Total Customers"
          value={(summary?.total_customers ?? 0).toLocaleString()}
          subtext="Unique customer IDs"
          icon={<Users className="h-4 w-4" />}
          variant="info"
        />
        <StatCard
          label="Avg Orders / Customer"
          value={(summary?.avg_orders_per_customer ?? 0).toFixed(2)}
          subtext="Purchase frequency"
          icon={<ShoppingCart className="h-4 w-4" />}
          variant="default"
        />
        <StatCard
          label="Avg Spend / Customer"
          value={fmtCurrency(summary?.avg_spend_per_customer ?? 0)}
          subtext="Lifetime average spend"
          icon={<DollarSign className="h-4 w-4" />}
          variant="success"
        />
      </div>

      {/* Purchase Frequency + Cohort row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Purchase Frequency */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5">
          <h3 className="text-sm font-semibold text-white mb-4">Purchase Frequency Distribution</h3>
          {frequency.length === 0 ? (
            <p className="text-xs text-slate-400">No frequency data available.</p>
          ) : (
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={frequency} margin={{ top: 4, right: 16, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="order_count" tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={false} label={{ value: 'No. of Orders', position: 'insideBottom', fill: '#64748b', fontSize: 11, dy: 8 }} />
                  <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={false} tickFormatter={(v) => v.toLocaleString()} />
                  <Tooltip
                    contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8, fontSize: 12 }}
                    formatter={(v: number) => [v.toLocaleString(), 'Customers']}
                  />
                  <Bar dataKey="num_customers" fill="#6366f1" radius={[4, 4, 0, 0]} name="Customers" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        {/* Monthly New Customers (Cohort) */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5">
          <h3 className="text-sm font-semibold text-white mb-4">Monthly New Customers</h3>
          {cohort.length === 0 ? (
            <p className="text-xs text-slate-400">No cohort data available.</p>
          ) : (
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={cohort} margin={{ top: 4, right: 16, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="month" tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={false} />
                  <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={false} tickFormatter={(v) => v.toLocaleString()} />
                  <Tooltip
                    contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8, fontSize: 12 }}
                    formatter={(v: number) => [v.toLocaleString(), 'New Customers']}
                  />
                  <Line type="monotone" dataKey="new_customers" stroke="#22d3ee" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      </div>

      {/* Top States */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5">
        <h3 className="text-sm font-semibold text-white mb-4">Customers by State</h3>
        {states.length === 0 ? (
          <p className="text-xs text-slate-400">No state data available.</p>
        ) : (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={states} margin={{ top: 4, right: 16, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="state" tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={false} />
                <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={false} tickFormatter={(v) => v.toLocaleString()} />
                <Tooltip
                  contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8, fontSize: 12 }}
                  formatter={(v: number) => [v.toLocaleString(), 'Customers']}
                />
                <Bar dataKey="customer_count" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
};
