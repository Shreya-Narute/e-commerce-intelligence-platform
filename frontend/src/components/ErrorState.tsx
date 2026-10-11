import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  className?: string;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Service Error Encountered',
  message,
  onRetry,
  className = '',
}) => {
  return (
    <div
      className={`flex flex-col items-center justify-center p-10 text-center rounded-xl border border-red-900/50 bg-red-950/20 backdrop-blur-sm ${className}`}
    >
      <div className="h-12 w-12 rounded-full bg-red-950/80 border border-red-800/60 flex items-center justify-center text-red-400 mb-4 shadow-inner">
        <AlertTriangle className="h-6 w-6" />
      </div>
      <h3 className="text-base font-semibold text-red-200">{title}</h3>
      <p className="text-xs text-red-300/80 mt-1 max-w-md break-words">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-5 inline-flex items-center gap-2 px-4 py-2 text-xs font-medium rounded-lg bg-red-900/60 text-red-100 border border-red-700/50 hover:bg-red-800/80 transition-colors"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          Retry Request
        </button>
      )}
    </div>
  );
};
