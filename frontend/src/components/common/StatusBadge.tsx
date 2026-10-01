import React from 'react';
import clsx from 'clsx';
import { SeverityLevel } from '../../types';
import { ShieldCheck, AlertCircle, AlertTriangle, ShieldAlert } from 'lucide-react';

interface StatusBadgeProps {
  severity: SeverityLevel | string;
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  severity,
  size = 'md',
  showIcon = true,
}) => {
  const norm = (severity || 'SAFE').toUpperCase();

  const config: Record<
    string,
    { bg: string; text: string; border: string; icon: React.ReactNode; label: string }
  > = {
    SAFE: {
      bg: 'bg-emerald-500/10',
      text: 'text-emerald-400',
      border: 'border-emerald-500/30',
      icon: <ShieldCheck className="w-3.5 h-3.5" />,
      label: 'SAFE',
    },
    MODERATE: {
      bg: 'bg-amber-500/10',
      text: 'text-amber-400',
      border: 'border-amber-500/30',
      icon: <AlertTriangle className="w-3.5 h-3.5" />,
      label: 'MODERATE',
    },
    ATTENTION: {
      bg: 'bg-amber-500/10',
      text: 'text-amber-400',
      border: 'border-amber-500/30',
      icon: <AlertTriangle className="w-3.5 h-3.5" />,
      label: 'ATTENTION',
    },
    HIGH: {
      bg: 'bg-orange-500/15',
      text: 'text-orange-400',
      border: 'border-orange-500/40',
      icon: <AlertCircle className="w-3.5 h-3.5" />,
      label: 'HIGH RISK',
    },
    'HIGH RISK': {
      bg: 'bg-orange-500/15',
      text: 'text-orange-400',
      border: 'border-orange-500/40',
      icon: <AlertCircle className="w-3.5 h-3.5" />,
      label: 'HIGH RISK',
    },
    CRITICAL: {
      bg: 'bg-red-500/20',
      text: 'text-red-400',
      border: 'border-red-500/50',
      icon: <ShieldAlert className="w-3.5 h-3.5" />,
      label: 'CRITICAL',
    },
  };

  const item = config[norm] || config.SAFE;

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 gap-1',
    md: 'text-xs px-2.5 py-1 gap-1.5 font-medium',
    lg: 'text-sm px-3.5 py-1.5 gap-2 font-semibold',
  };

  return (
    <span
      className={clsx(
        'inline-flex items-center rounded-full border tracking-wide uppercase',
        item.bg,
        item.text,
        item.border,
        sizeClasses[size]
      )}
    >
      {showIcon && item.icon}
      <span>{item.label}</span>
    </span>
  );
};
