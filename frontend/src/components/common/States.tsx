import React from 'react';
import clsx from 'clsx';
import { Shield, AlertTriangle, RefreshCw } from 'lucide-react';

export const LoadingSpinner: React.FC<{ size?: 'sm' | 'md' | 'lg'; text?: string }> = ({
  size = 'md',
  text,
}) => {
  const sizeMap = {
    sm: 'w-4 h-4 border-2',
    md: 'w-8 h-8 border-2',
    lg: 'w-12 h-12 border-3',
  };

  return (
    <div className="flex flex-col items-center justify-center p-6 gap-3">
      <div
        className={clsx(
          'rounded-full border-t-cyan-400 border-r-cyan-400 border-b-transparent border-l-transparent animate-spin',
          sizeMap[size]
        )}
      />
      {text && <p className="text-xs text-slate-400 font-mono tracking-wider">{text}</p>}
    </div>
  );
};

export const EmptyState: React.FC<{
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: React.ReactNode;
}> = ({ icon, title, description, action }) => {
  return (
    <div className="flex flex-col items-center justify-center text-center p-8 glass-card border-dashed border-white/10 my-4">
      <div className="w-12 h-12 rounded-xl bg-slate-800/80 border border-white/5 flex items-center justify-center text-cyan-400 mb-3 shadow-[0_0_15px_rgba(0,168,255,0.1)]">
        {icon || <Shield className="w-6 h-6 opacity-70" />}
      </div>
      <h3 className="text-sm font-semibold text-slate-200 mb-1">{title}</h3>
      {description && <p className="text-xs text-slate-400 max-w-sm mb-4 leading-relaxed">{description}</p>}
      {action}
    </div>
  );
};

export const ErrorState: React.FC<{
  message?: string;
  onRetry?: () => void;
}> = ({ message = 'An unexpected error occurred while loading security data.', onRetry }) => {
  return (
    <div className="flex flex-col items-center justify-center text-center p-8 glass-card border-red-500/20 my-4 bg-red-950/10">
      <div className="w-12 h-12 rounded-xl bg-red-500/10 border border-red-500/20 flex items-center justify-center text-red-400 mb-3">
        <AlertTriangle className="w-6 h-6" />
      </div>
      <h3 className="text-sm font-semibold text-red-200 mb-1">Security System Alert</h3>
      <p className="text-xs text-slate-400 max-w-sm mb-4">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-xs font-medium text-slate-300 border border-white/10 transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Retry Request
        </button>
      )}
    </div>
  );
};

export const DemoBanner: React.FC = () => {
  return (
    <div className="bg-gradient-to-r from-blue-950/40 via-cyan-950/20 to-purple-950/40 border-b border-cyan-500/20 px-4 py-1.5 text-xs text-slate-400 flex items-center justify-between">
      <div className="flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
        <span className="font-mono text-[11px] text-cyan-300 font-semibold tracking-wide">
          DEMO ENVIRONMENT ACTIVE
        </span>
        <span className="text-slate-500 hidden sm:inline">|</span>
        <span className="text-slate-400 hidden sm:inline text-[11px]">
          Multi-User Controlled Child Safety Testing Platform
        </span>
      </div>
      <div className="font-mono text-[11px] text-slate-400">
        Demo Password: <span className="text-cyan-300 font-semibold">demo123</span>
      </div>
    </div>
  );
};
