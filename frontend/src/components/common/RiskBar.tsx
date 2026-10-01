import React from 'react';
import clsx from 'clsx';

interface RiskBarProps {
  score: number;
  label?: string;
  sublabel?: string;
  showPercentage?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const RiskBar: React.FC<RiskBarProps> = ({
  score,
  label,
  sublabel,
  showPercentage = true,
  size = 'md',
  className,
}) => {
  const clampedScore = Math.max(0, Math.min(100, Math.round(score)));

  const getBarColor = (val: number) => {
    if (val <= 29) return 'bg-gradient-to-r from-emerald-500 to-teal-400';
    if (val <= 59) return 'bg-gradient-to-r from-amber-500 to-yellow-400';
    if (val <= 79) return 'bg-gradient-to-r from-orange-500 to-amber-500';
    return 'bg-gradient-to-r from-red-600 to-pink-600 shadow-[0_0_12px_rgba(255,23,68,0.5)]';
  };

  const getScoreColor = (val: number) => {
    if (val <= 29) return 'text-emerald-400';
    if (val <= 59) return 'text-amber-400';
    if (val <= 79) return 'text-orange-400';
    return 'text-red-400 font-bold';
  };

  const heightClasses = {
    sm: 'h-1.5',
    md: 'h-2.5',
    lg: 'h-4',
  };

  return (
    <div className={clsx('w-full', className)}>
      {(label || showPercentage) && (
        <div className="flex justify-between items-center mb-1.5 text-xs">
          <div className="flex items-center gap-2">
            {label && <span className="font-medium text-slate-300">{label}</span>}
            {sublabel && <span className="text-slate-500 text-[11px]">{sublabel}</span>}
          </div>
          {showPercentage && (
            <span className={clsx('font-semibold font-mono', getScoreColor(clampedScore))}>
              {clampedScore}%
            </span>
          )}
        </div>
      )}
      <div className={clsx('w-full bg-slate-800/80 rounded-full overflow-hidden p-0.5 border border-white/5', heightClasses[size])}>
        <div
          className={clsx('h-full rounded-full transition-all duration-700 ease-out', getBarColor(clampedScore))}
          style={{ width: `${clampedScore}%` }}
        />
      </div>
    </div>
  );
};
