import React from 'react';

interface StatCardProps {
  label: string;
  value: string | number;
  subtext?: string;
  icon?: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'info';
}

export const StatCard: React.FC<StatCardProps> = ({
  label,
  value,
  subtext,
  icon,
  variant = 'default',
}) => {
  const borderStyles = {
    default: 'border-slate-800 hover:border-slate-700',
    success: 'border-emerald-900/50 hover:border-emerald-800/60',
    warning: 'border-amber-900/50 hover:border-amber-800/60',
    info: 'border-indigo-900/50 hover:border-indigo-800/60',
  }[variant];

  return (
    <div
      className={`p-5 rounded-xl bg-slate-900/60 border ${borderStyles} transition-all duration-200 flex flex-col justify-between`}
    >
      <div className="flex items-center justify-between gap-2">
        <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">{label}</span>
        {icon && <div className="text-slate-400">{icon}</div>}
      </div>
      <div className="mt-3">
        <div className="text-2xl font-bold tracking-tight text-white">{value}</div>
        {subtext && <div className="text-[11px] text-slate-400 mt-1">{subtext}</div>}
      </div>
    </div>
  );
};
