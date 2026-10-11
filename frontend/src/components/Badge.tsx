import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'healthy' | 'degraded' | 'warning' | 'info' | 'neutral';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'neutral',
  className = '',
}) => {
  const styles = {
    healthy: 'bg-emerald-950/60 text-emerald-400 border-emerald-800/50',
    degraded: 'bg-red-950/60 text-red-400 border-red-800/50',
    warning: 'bg-amber-950/60 text-amber-400 border-amber-800/50',
    info: 'bg-indigo-950/60 text-indigo-400 border-indigo-800/50',
    neutral: 'bg-slate-800/70 text-slate-300 border-slate-700/60',
  }[variant];

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border ${styles} ${className}`}
    >
      <span className="h-1.5 w-1.5 rounded-full bg-current opacity-80" />
      {children}
    </span>
  );
};
