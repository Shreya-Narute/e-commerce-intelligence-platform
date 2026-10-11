import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingStateProps {
  message?: string;
  subtext?: string;
  className?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  message = 'Loading platform data...',
  subtext = 'Fetching verified records from PostgreSQL engine',
  className = '',
}) => {
  return (
    <div
      className={`flex flex-col items-center justify-center p-12 text-center rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-sm ${className}`}
    >
      <Loader2 className="h-9 w-9 text-indigo-500 animate-spin mb-4" />
      <h3 className="text-base font-semibold text-slate-200">{message}</h3>
      {subtext && <p className="text-xs text-slate-400 mt-1 max-w-sm">{subtext}</p>}
    </div>
  );
};
