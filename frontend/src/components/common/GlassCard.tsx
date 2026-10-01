import React from 'react';
import clsx from 'clsx';

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  className?: string;
  glow?: 'blue' | 'purple' | 'red' | 'green' | 'none';
  hover?: boolean;
}

export const GlassCard: React.FC<GlassCardProps> = ({
  children,
  className,
  glow = 'none',
  hover = false,
  ...props
}) => {
  const glowStyles = {
    blue: 'border-cyan-500/30 shadow-[0_0_20px_rgba(0,168,255,0.15)]',
    purple: 'border-purple-500/30 shadow-[0_0_20px_rgba(124,58,237,0.15)]',
    red: 'border-red-500/30 shadow-[0_0_20px_rgba(255,23,68,0.2)]',
    green: 'border-emerald-500/30 shadow-[0_0_20px_rgba(0,230,118,0.15)]',
    none: '',
  };

  return (
    <div
      className={clsx(
        'glass-card p-5 relative overflow-hidden transition-all duration-300',
        hover && 'glass-card-hover',
        glowStyles[glow],
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};
