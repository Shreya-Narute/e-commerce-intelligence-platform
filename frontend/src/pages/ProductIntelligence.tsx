import React, { useEffect, useState } from 'react';
import {
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
import { Package } from 'lucide-react';
import { LoadingState } from '../components/LoadingState';
import { ErrorState } from '../components/ErrorState';
import { EmptyState } from '../components/EmptyState';
import { getTopRevenueProducts, getCategories } from '../services/productsService';
import { ProductRevenue, CategoryStats } from '../types/products';

const CHART_COLORS = ['#6366f1', '#22d3ee', '#f59e0b', '#10b981', '#f43f5e', '#a78bfa', '#34d399', '#fb923c', '#60a5fa', '#e879f9'];

const fmtCurrency = (v: number) =>
  new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(v);

type SortKey = 'revenue' | 'order_count';

export const ProductIntelligence: React.FC = () => {
  const [products, setProducts] = useState<ProductRevenue[]>([]);
  const [categories, setCategories] = useState<CategoryStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sortKey, setSortKey] = useState<SortKey>('revenue');
  const [sortAsc, setSortAsc] = useState(false);

  const fetchAll = async () => {
    setLoading(true);
    setError(null);
    try {
      const [p, c] = await Promise.all([getTopRevenueProducts(), getCategories()]);
      setProducts(p.slice(0, 20));
      setCategories(c);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load product data';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAll(); }, []);

  const toggleSort = (key: SortKey) => {
    if (sortKey === key) setSortAsc(!sortAsc);
    else { setSortKey(key); setSortAsc(false); }
  };

  const sortedCategories = [...categories].sort((a, b) => {
    const diff = (a[sortKey] as number) - (b[sortKey] as number);
    return sortAsc ? diff : -diff;
  });

  if (loading) return <LoadingState message="Loading Product Intelligence..." subtext="Analysing product revenue and category performance" />;
  if (error) return <ErrorState title="Product Data Unavailable" message={error} onRetry={fetchAll} />;
  if (products.length === 0 && categories.length === 0) {
    return (
      <EmptyState
        title="No Product Data Available"
        description="The products and order_items tables are empty. Run the ingestion pipeline first."
        stageBadge="Product Intelligence"
        actionText="View Data Quality"
        actionLink="/data-quality"
        icon={<Package className="h-7 w-7 text-indigo-400" />}
      />
    );
  }

  const topPieCats = categories.slice(0, 10);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="pb-2 border-b border-slate-800">
        <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 mb-2">
          Product Intelligence
        </div>
        <h2 className="text-xl font-bold text-white tracking-tight">Product & Category Analysis</h2>
        <p className="text-xs text-slate-400 mt-0.5">Category profitability, top products by revenue, and category distribution.</p>
      </div>

      {/* Top Products Horizontal Bar */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5">
        <h3 className="text-sm font-semibold text-white mb-4">Top 20 Products by Revenue</h3>
        {products.length === 0 ? (
          <p className="text-xs text-slate-400">No product revenue data available.</p>
        ) : (
          <div className="h-96">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={products}
                layout="vertical"
                margin={{ top: 4, right: 24, left: 130, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                <XAxis type="number" tick={{ fill: '#94a3b8', fontSize: 11 }} tickLine={false} axisLine={false} tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`} />
                <YAxis
                  type="category"
                  dataKey="product_id"
                  tick={{ fill: '#94a3b8', fontSize: 10 }}
                  tickLine={false}
                  axisLine={false}
                  width={125}
                  tickFormatter={(v: string) => v.substring(0, 12) + '…'}
                />
                <Tooltip
                  contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8, fontSize: 12 }}
                  formatter={(v: number) => [fmtCurrency(v), 'Revenue']}
                  labelFormatter={(l: string) => `Product: ${l}`}
                />
                <Bar dataKey="revenue" fill="#6366f1" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Category PieChart + Table row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Pie */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5">
          <h3 className="text-sm font-semibold text-white mb-4">Category Revenue Share (Top 10)</h3>
          {topPieCats.length === 0 ? (
            <p className="text-xs text-slate-400">No category data available.</p>
          ) : (
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={topPieCats}
                    dataKey="revenue"
                    nameKey="category_name"
                    cx="50%"
                    cy="50%"
                    outerRadius={90}
                    label={false}
                  >
                    {topPieCats.map((_, i) => (
                      <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8, fontSize: 12 }}
                    formatter={(v: number) => [fmtCurrency(v), 'Revenue']}
                  />
                  <Legend wrapperStyle={{ fontSize: 11, color: '#94a3b8' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        {/* Category sortable table */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden">
          <div className="p-5 border-b border-slate-800">
            <h3 className="text-sm font-semibold text-white">Category Performance Table</h3>
          </div>
          <div className="overflow-x-auto max-h-72 overflow-y-auto">
            <table className="w-full text-xs text-left text-slate-300">
              <thead className="bg-slate-950/80 text-[11px] uppercase tracking-wider text-slate-400 border-b border-slate-800 sticky top-0">
                <tr>
                  <th className="py-3 px-4">Category</th>
                  {(['revenue', 'order_count'] as SortKey[]).map((k) => (
                    <th
                      key={k}
                      className="py-3 px-4 cursor-pointer hover:text-white select-none"
                      onClick={() => toggleSort(k)}
                    >
                      {k === 'revenue' ? 'Revenue' : 'Orders'}
                      {sortKey === k ? (sortAsc ? ' ↑' : ' ↓') : ''}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {sortedCategories.map((cat, i) => (
                  <tr key={i} className="hover:bg-slate-800/30">
                    <td className="py-2.5 px-4 font-medium text-slate-200 truncate max-w-[140px]">{cat.category_name}</td>
                    <td className="py-2.5 px-4 font-mono">{fmtCurrency(cat.revenue)}</td>
                    <td className="py-2.5 px-4 font-mono">{cat.order_count.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
